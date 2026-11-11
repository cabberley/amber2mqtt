"""Regression tests for the AEMO dashboard collector."""

import json
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import patch

import requests

import aemodata
from const import AEMO_NEM_SUMMARY_URI


BASE_URL = "https://dashboards.public.aemo.com.au"
MARKET_TIME = timezone(timedelta(hours=10))
REGIONS = ("NSW1", "QLD1", "SA1", "TAS1", "VIC1")


def summary_payload():
    return {
        "data": {
            "summary": [
                {
                    "settlementDate": "2026-11-11T11:05:00+10:00",
                    "regionId": region,
                    "price": -50,
                    "priceStatus": "FIRM",
                    "apcFlag": 0,
                    "marketsuspendedFlag": 0,
                    "totalDemand": 7000,
                    "netInterchange": -100,
                    "scheduledGeneration": 4000,
                    "semischeduledGeneration": 3000,
                    "interconnectorFlows": json.dumps([{
                        "name": "NSW1-QLD1", "value": -100,
                        "exportlimit": 500, "importlimit": -600,
                    }]),
                }
                for region in REGIONS
            ],
            "prices": [{"regionId": region, "rrp": None} for region in REGIONS],
        },
        "errors": [],
    }


def response(payload, status=200):
    result = requests.Response()
    result.status_code = status
    result._content = json.dumps(payload).encode()
    result.url = AEMO_NEM_SUMMARY_URI
    return result


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.key_patch = patch.object(aemodata, "_aemoApiKey", None, create=True)
        self.key_patch.start()
        self.addCleanup(self.key_patch.stop)
        self.get_patch = patch.object(aemodata.http_session, "get")
        self.get = self.get_patch.start()
        self.addCleanup(self.get_patch.stop)

    def queue_payload(self, payload):
        aemodata._aemoApiKey = None
        self.get.side_effect = [
            response({"xApiKey": "test-key"}),
            response(payload),
        ]

    def test_dashboard_mapping_preserves_mqtt_contract_and_caches_key(self):
        payload = summary_payload()
        self.get.side_effect = [
            response({"xApiKey": "test-key"}),
            response(payload),
            response(payload),
        ]
        first = aemodata.getAemoCurrentData()
        snapshot = deepcopy(first)
        second = aemodata.getAemoCurrentData()
        self.assertEqual(first, snapshot)
        self.assertEqual(second, snapshot)
        self.assertEqual(set(first), {"ELEC_NEM_SUMMARY"})
        self.assertEqual(len(first["ELEC_NEM_SUMMARY"]), 5)
        self.assertEqual(
            {record["REGIONID"] for record in first["ELEC_NEM_SUMMARY"]}, set(REGIONS)
        )
        for record in first["ELEC_NEM_SUMMARY"]:
            self.assertEqual(set(record), {
                "SETTLEMENTDATE", "REGIONID", "PRICE", "PRICE_STATUS", "APCFLAG",
                "MARKETSUSPENDEDFLAG", "TOTALDEMAND", "NETINTERCHANGE",
                "SCHEDULEDGENERATION", "SEMISCHEDULEDGENERATION", "INTERCONNECTORFLOWS",
            })
            self.assertEqual(record["PRICE"], -50)
            self.assertEqual(record["PRICE_STATUS"], "FIRM")
            self.assertEqual(record["SETTLEMENTDATE"], "2026-11-11T11:05:00")
            self.assertEqual(record["INTERCONNECTORFLOWS"], [{
                "name": "NSW1-QLD1", "value": -100,
                "exportlimit": 500, "importlimit": -600,
            }])
        self.assertEqual(self.get.call_args_list[0].args, (BASE_URL + "/config.json",))
        for call in self.get.call_args_list[1:]:
            self.assertEqual(
                call.args, (BASE_URL + "/NEM/v1/PWS/NEMDashboard/elecSummary",)
            )
            self.assertEqual(call.kwargs["headers"]["x-api-key"], "test-key")
            self.assertEqual(call.kwargs["timeout"], 30)

    def test_summary_timestamp_offsets_and_empty_flows(self):
        payload = summary_payload()
        payload["data"]["summary"][0]["settlementDate"] = "2026-11-11T12:05:00+11:00"
        payload["data"]["summary"][0]["interconnectorFlows"] = "[]"
        self.queue_payload(payload)
        record = aemodata.getAemoCurrentData()["ELEC_NEM_SUMMARY"][0]
        self.assertEqual(record["SETTLEMENTDATE"], "2026-11-11T11:05:00")
        self.assertEqual(record["INTERCONNECTORFLOWS"], [])

    def test_incomplete_or_duplicate_regions_are_rejected(self):
        missing = summary_payload()
        missing["data"]["summary"].pop()
        duplicate = summary_payload()
        duplicate["data"]["summary"][-1] = deepcopy(duplicate["data"]["summary"][0])
        for payload in (missing, duplicate):
            with self.subTest(payload=payload):
                self.queue_payload(payload)
                with self.assertRaises(requests.exceptions.RequestException):
                    aemodata.getAemoCurrentData()

    def test_expired_key_is_refreshed_once(self):
        for failure in (
            response({}, 401),
            response({}, 403),
            response({"errors": [{"code": "401"}]}),
            response({"errors": [{"code": 403}]}),
        ):
            with self.subTest(status=failure.status_code, body=failure.text):
                aemodata._aemoApiKey = None
                self.get.reset_mock()
                self.get.side_effect = [
                    response({"xApiKey": "old-key"}), failure,
                    response({"xApiKey": "new-key"}), response(summary_payload()),
                ]
                self.assertEqual(len(aemodata.getAemoCurrentData()["ELEC_NEM_SUMMARY"]), 5)
                self.assertEqual(self.get.call_count, 4)
                self.assertEqual(self.get.call_args.kwargs["headers"]["x-api-key"], "new-key")

    def test_repeated_auth_failure_is_not_retried_indefinitely(self):
        self.get.side_effect = [
            response({"xApiKey": "old-key"}), response({}, 403),
            response({"xApiKey": "new-key"}), response({}, 403),
        ]
        with self.assertRaises(requests.exceptions.RequestException):
            aemodata.getAemoCurrentData()
        self.assertEqual(self.get.call_count, 4)
        self.assertIsNone(aemodata._aemoApiKey)

    def test_invalid_key_and_transport_errors_are_explicit(self):
        for config in ({}, {"xApiKey": ""}, {"xApiKey": 123}):
            with self.subTest(config=config):
                self.get.side_effect = [response(config)]
                with self.assertRaises(requests.exceptions.RequestException):
                    aemodata.getAemoCurrentData()
        self.get.side_effect = requests.exceptions.Timeout("timed out")
        with self.assertRaisesRegex(requests.exceptions.RequestException, "API request failed"):
            aemodata.getAemoCurrentData()

    def test_failed_config_and_failed_key_refresh_recover_next_poll(self):
        for prefix in (
            [requests.exceptions.Timeout("config timed out")],
            [
                response({"xApiKey": "old-key"}), response({}, 403),
                requests.exceptions.ConnectionError("refresh failed"),
            ],
        ):
            with self.subTest(prefix=prefix):
                aemodata._aemoApiKey = None
                self.get.side_effect = prefix + [
                    response({"xApiKey": "new-key"}), response(summary_payload()),
                ]
                with self.assertRaises(requests.exceptions.RequestException):
                    aemodata.getAemoCurrentData()
                self.assertIsNone(aemodata._aemoApiKey)
                self.assertEqual(len(aemodata.getAemoCurrentData()["ELEC_NEM_SUMMARY"]), 5)

    def test_failed_dashboard_response_recovers_with_cached_key(self):
        malformed = response({})
        malformed._content = b"invalid JSON"
        for failure in (
            requests.exceptions.Timeout("dashboard timed out"),
            response({}, 503), malformed,
            response({"data": {"summary": []}}),
        ):
            with self.subTest(failure=failure):
                aemodata._aemoApiKey = "cached-key"
                self.get.reset_mock()
                self.get.side_effect = [failure, response(summary_payload())]
                with self.assertRaises(requests.exceptions.RequestException):
                    aemodata.getAemoCurrentData()
                self.assertEqual(len(aemodata.getAemoCurrentData()["ELEC_NEM_SUMMARY"]), 5)
                self.assertEqual(self.get.call_count, 2)
                self.assertEqual(self.get.call_args.kwargs["headers"]["x-api-key"], "cached-key")

    def test_invalid_dashboard_responses_are_rejected(self):
        bad_json = response({})
        bad_json._content = b"not JSON"
        for invalid in (
            bad_json, response({}, 500), response([]),
            response({"errors": "invalid"}),
            response({"errors": [{"code": "500", "message": "unavailable"}]}),
            response({}), response({"data": {"summary": []}}),
        ):
            with self.subTest(body=invalid.text):
                aemodata._aemoApiKey = None
                self.get.side_effect = [response({"xApiKey": "test-key"}), invalid]
                with self.assertRaises(requests.exceptions.RequestException):
                    aemodata.getAemoCurrentData()


    def test_invalid_summary_fields_are_rejected(self):
        for field, value in (
            ("price", None), ("price", True), ("totalDemand", float("nan")),
            ("regionId", "BAD"), ("settlementDate", "invalid"),
            ("apcFlag", 2), ("interconnectorFlows", "not JSON"),
            ("interconnectorFlows", "{}"),
            ("interconnectorFlows", '[{"name": "incomplete"}]'),
        ):
            with self.subTest(field=field, value=value):
                aemodata._aemoApiKey = None
                payload = summary_payload()
                payload["data"]["summary"][0][field] = value
                self.queue_payload(payload)
                with self.assertRaises(requests.exceptions.RequestException):
                    aemodata.getAemoCurrentData()
        payload = summary_payload()
        del payload["data"]["summary"][0]["priceStatus"]
        self.queue_payload(payload)
        with self.assertRaises(requests.exceptions.RequestException):
            aemodata.getAemoCurrentData()


class RetryTests(unittest.TestCase):
    def test_server_retry_after_is_bounded_and_next_poll_recovers(self):
                failures = []

                class Handler(BaseHTTPRequestHandler):
                    def do_GET(self):
                        if self.path == "/config":
                            payload, status = {"xApiKey": "test-key"}, 200
                        elif len(failures) < 4:
                            failures.append(self.path)
                            payload, status = {}, 503
                        else:
                            payload, status = summary_payload(), 200
                        body = json.dumps(payload).encode()
                        self.send_response(status)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(body)))
                        if status == 503:
                            self.send_header("Retry-After", "3600")
                        self.end_headers()
                        self.wfile.write(body)

                    def log_message(self, format, *args):
                        pass

                with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
                    thread = Thread(target=server.serve_forever)
                    thread.start()
                    base = f"http://127.0.0.1:{server.server_port}"
                    try:
                        with (
                            patch.object(aemodata, "_aemoApiKey", None),
                            patch.object(aemodata, "AEMO_CONFIG_URI", base + "/config"),
                            patch.object(aemodata, "AEMO_NEM_SUMMARY_URI", base + "/summary"),
                            patch("urllib3.util.retry.time.sleep") as sleep,
                        ):
                            with self.assertRaises(requests.exceptions.RequestException):
                                aemodata.getAemoCurrentData()
                            waits = [call.args[0] for call in sleep.call_args_list]
                            self.assertTrue(waits)
                            self.assertLessEqual(max(waits), 5)
                            self.assertEqual(len(failures), 4)
                            self.assertEqual(len(aemodata.getAemoCurrentData()["ELEC_NEM_SUMMARY"]), 5)
                    finally:
                        server.shutdown()
                        thread.join(timeout=5)

class SettlementTests(unittest.TestCase):
    def test_only_current_firm_interval_is_accepted_in_market_time(self):
        cases = (
            ("2026-11-11T11:05:00", "2026-11-11T11:01:00+10:00", "FIRM", True),
            ("2026-11-11T11:05:00+10:00", "2026-11-11T01:01:00+00:00", "FIRM", True),
            ("2026-11-11T12:05:00+11:00", "2026-11-11T11:01:00+10:00", "FIRM", True),
            ("2026-11-11T12:00:00", "2026-11-11T11:59:00+10:00", "FIRM", True),
            ("2026-11-12T00:00:00", "2026-11-11T23:59:00+10:00", "FIRM", True),
            ("2026-11-10T11:05:00", "2026-11-11T11:01:00+10:00", "FIRM", False),
            ("2026-11-11T10:05:00", "2026-11-11T11:01:00+10:00", "FIRM", False),
            ("2026-11-11T11:10:00", "2026-11-11T11:01:00+10:00", "FIRM", False),
            ("2026-11-11T11:05:00", "2026-11-11T11:05:00+10:00", "FIRM", False),
            ("2026-11-11T11:05:00", "2026-11-11T11:00:00+10:00", "FIRM", True),
            ("2026-11-11T11:05:00", "2026-11-11T11:01:00+10:00", "PRELIM", False),
        )
        for settlement, now, status, expected in cases:
            with self.subTest(settlement=settlement, now=now, status=status):
                with patch.object(aemodata, "datetime", wraps=datetime) as clock:
                    clock.now.return_value = datetime.fromisoformat(now)
                    result = aemodata.checkAemoSettlementDate({
                        "SETTLEMENTDATE": settlement, "PRICE_STATUS": status,
                    })
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
