"""Amber HTTP retry and recovery regression tests."""

import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from amberelectric.models.current_interval import CurrentInterval
from amberelectric.models.price_descriptor import PriceDescriptor
from amberelectric.models.spike_status import SpikeStatus
from amberelectric.rest import ApiException
from urllib3.exceptions import ReadTimeoutError

import amberdata


def current_interval():
    now = datetime.fromisoformat("2026-11-11T11:00:00+10:00")
    return CurrentInterval(
        type="CurrentInterval", duration=5, spotPerKwh=0.1, perKwh=10.0,
        date=now.date(), nemTime=now, startTime=now, endTime=now,
        renewables=25.0, channelType="general",
        spikeStatus=next(iter(SpikeStatus)),
        descriptor=next(iter(PriceDescriptor)), estimate=False,
    )


class AmberRetryTests(unittest.TestCase):
    def test_transient_http_and_transport_failures_retry_and_recover(self):
        interval = current_interval()
        for failure in (
            ApiException(status=503, reason="unavailable"),
            ReadTimeoutError(None, "/prices", "timed out"),
        ):
            with self.subTest(failure=type(failure).__name__):
                with (
                    patch.object(amberdata.amberelectric, "ApiClient") as client,
                    patch.object(amberdata.amberelectric.AmberApi, "get_current_prices") as get,
                    patch.object(amberdata.time, "sleep") as sleep,
                ):
                    get.side_effect = [failure, [SimpleNamespace(actual_instance=interval)]]
                    result = amberdata.getAmberData("unused", "site", 13, 5, 5)
                    self.assertIs(result["current"]["general"], interval)
                    self.assertEqual(get.call_count, 2)
                    sleep.assert_called_once_with(5)
                    self.assertEqual(client.call_args.args[0].retries, 0)
                    for call in get.call_args_list:
                        self.assertEqual(call.kwargs["_request_timeout"], 30)

    def test_exhausted_retries_do_not_poison_next_cycle(self):
        interval = current_interval()
        with (
            patch.object(amberdata.amberelectric.AmberApi, "get_current_prices") as get,
            patch.object(amberdata.time, "sleep") as sleep,
        ):
            get.side_effect = [
                ReadTimeoutError(None, "/prices", "timed out"),
                ReadTimeoutError(None, "/prices", "timed out"),
                ReadTimeoutError(None, "/prices", "timed out"),
                [SimpleNamespace(actual_instance=interval)],
            ]
            with self.assertRaises(ReadTimeoutError):
                amberdata.getAmberData("unused", "site", 13, 5, 0)
            self.assertEqual(get.call_count, 3)
            self.assertEqual([call.args[0] for call in sleep.call_args_list], [5, 5])
            result = amberdata.getAmberData("unused", "site", 13, 5, 0)
            self.assertIs(result["current"]["general"], interval)
            self.assertEqual(get.call_count, 4)
            self.assertEqual(get.call_args.kwargs["_request_timeout"], 30)


if __name__ == "__main__":
    unittest.main()
