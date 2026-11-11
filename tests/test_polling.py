"""Polling completion, MQTT failure and scheduler recovery tests."""

import importlib.util
import json
import unittest
from pathlib import Path
from threading import Event
from types import SimpleNamespace
from unittest.mock import Mock, mock_open, patch

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from amberelectric.rest import ApiException
import requests


def load_app():
    config = {
        "amber": {
            "site_id": "unused", "access_token": "unused",
            "amber5minPrice_seconds": "15", "amber5minPrice_minutes": "*",
        },
        "aemo": {"aemo5minPrice_seconds": "15", "aemo5minPrice_minutes": "*"},
        "integration": {"amber2mqtt": "True"},
        "mqtt": {"debug": "False", "broker": "localhost", "port": 1883, "client_id": "test"},
    }
    spec = importlib.util.spec_from_file_location(
        "polling_test_app", Path(__file__).resolve().parents[1] / "app.py"
    )
    module = importlib.util.module_from_spec(spec)
    with (
        patch("builtins.open", mock_open(read_data=json.dumps(config))),
        patch("os.path.isfile", return_value=False),
    ):
        spec.loader.exec_module(module)
    module.client = Mock()
    return module


class PollingTests(unittest.TestCase):
    def setUp(self):
        self.app = load_app()
        self.amber_data = {"current": {"general": SimpleNamespace(estimate=False)}}
        self.aemo_data = {"ELEC_NEM_SUMMARY": [{}]}
        self.get_amber = self.patch(self.app.al, "getAmberData", return_value=self.amber_data)
        self.get_aemo = self.patch(self.app.aemo, "getAemoCurrentData", return_value=self.aemo_data)
        self.patch(self.app.aemo, "checkAemoSettlementDate", return_value=True)
        self.publish_amber = self.patch(self.app.a2m, "publishAmberStateCurrent")
        self.patch(self.app.a2m, "publishAmberStatePeriods")
        self.patch(self.app.a2m, "publishAmberState5MinForecasts")
        self.publish_aemo = self.patch(self.app.a2m, "publishAemoStateCurrent")

    def patch(self, target, name, **kwargs):
        patcher = patch.object(target, name, **kwargs)
        result = patcher.start()
        self.addCleanup(patcher.stop)
        return result

    def test_failed_amber_forecast_is_retried_on_next_poll(self):
        self.app.amber5minForecast = True
        self.get_amber.side_effect = [
            self.amber_data, ApiException(status=503, reason="unavailable"),
            self.amber_data, self.amber_data,
        ]
        with self.assertRaises(ApiException):
            self.app.amber5minPrice()
        self.assertTrue(self.app.amberEstimatePrice)
        self.app.amber5minPrice()
        self.assertFalse(self.app.amberEstimatePrice)
        self.app.amber5minPrice()
        self.assertEqual(self.get_amber.call_count, 4)

    def test_failed_publish_does_not_mark_either_poll_complete(self):
        for job, publisher, flag, pending in (
            (self.app.aemo5MinCurrentPrice, self.publish_aemo, "aemoPriceFirm", False),
            (self.app.amber5minPrice, self.publish_amber, "amberEstimatePrice", True),
        ):
            with self.subTest(job=job.__name__):
                publisher.side_effect = [ConnectionError("MQTT disconnected"), None]
                with self.assertRaises(ConnectionError):
                    job()
                self.assertEqual(getattr(self.app, flag), pending)
                job()
                self.assertEqual(getattr(self.app, flag), not pending)
                self.assertEqual(publisher.call_count, 2)

    def test_previous_interval_completion_cannot_skip_next_interval(self):
        for job, get, data, reset in (
            (self.app.aemo5MinCurrentPrice, self.get_aemo, self.aemo_data,
             self.app.aemoResetPriceFirm),
            (self.app.amber5minPrice, self.get_amber, self.amber_data,
             self.app.amberResetEstimatePrice),
        ):
            with self.subTest(job=job.__name__):
                with patch.object(self.app.time, "time", return_value=600) as clock:
                    def slow_fetch(*args):
                        clock.return_value = 900
                        reset()
                        return data

                    get.side_effect = slow_fetch
                    job()
                    get.side_effect = None
                    job()
                self.assertEqual(get.call_count, 2)

    def test_scheduler_logs_failure_then_retries_both_jobs(self):
        for job, get, data, failure in (
            (self.app.aemo5MinCurrentPrice, self.get_aemo, self.aemo_data,
             requests.exceptions.Timeout("timed out")),
            (self.app.amber5minPrice, self.get_amber, self.amber_data,
             ApiException(status=503, reason="unavailable")),
        ):
            with self.subTest(job=job.__name__):
                recovered = Event()
                errors = []
                get.side_effect = [failure, data]

                def listener(event):
                    if event.exception:
                        errors.append(event.exception)
                    else:
                        recovered.set()

                scheduler = BackgroundScheduler()
                scheduler.add_listener(listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
                scheduler.add_job(job, "interval", seconds=0.02, max_instances=1)
                with self.assertLogs("apscheduler.executors.default", level="ERROR"):
                    scheduler.start()
                    try:
                        self.assertTrue(recovered.wait(timeout=5), "Polling did not recover")
                    finally:
                        scheduler.shutdown(wait=True)
                self.assertEqual(errors, [failure])
                self.assertEqual(get.call_count, 2)


class PublishTests(unittest.TestCase):
    def test_state_and_attribute_publish_failures_are_explicit_and_retryable(self):
        app = load_app()
        for publish, builder in (
            ("publishAemoStateCurrent", "aemoCurrentStateMessage"),
            ("publishAmberStateCurrent", "amberStateMessage"),
            ("publishAmberStatePeriods", "amberState5MinPeriods"),
            ("publishAmberState5MinForecasts", "amberState5MinForecasts"),
            ("publishAmberState30MinForecasts", "amberState30MinForecasts"),
            ("publishAmberStateUserForecasts", "amberStateUserForecasts"),
            ("publishAmberState5MinExtendedForecasts", "amberState5MinExtendedForecasts"),
        ):
            for failure_index in (0, 1):
                with self.subTest(publish=publish, failure_index=failure_index):
                    client = Mock()
                    client.publish.side_effect = (
                        [(0, 1)] * failure_index + [(4, 2)] + [(0, 1)] * 20
                    )
                    message = {"state": {}, "attributes": {"sample": {"value": 1}}}
                    with patch.object(app.a2m.mm, builder, return_value=message):
                        with self.assertRaisesRegex(ConnectionError, "Failed to send message"):
                            getattr(app.a2m, publish)(client, {})
                        client.publish.side_effect = None
                        client.publish.return_value = (0, 1)
                        getattr(app.a2m, publish)(client, {})


if __name__ == "__main__":
    unittest.main()
