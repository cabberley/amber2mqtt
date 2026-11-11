"""AEMO Module to poll NEM Report data"""

import json
from datetime import datetime, timedelta, timezone
from math import isfinite
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from const import (
    AEMO_CONFIG_URI,
    AEMO_NEM_SUMMARY_URI,
)

aemoPriceFirm = False

AEMO_MAX_RETRIES = 3
AEMO_RETRY_BACKOFF = 1 # seconds
AEMO_MAX_RETRY_DELAY = 5
AEMO_MARKET_TIME = timezone(timedelta(hours=10))
AEMO_REGIONS = {"NSW1", "QLD1", "SA1", "TAS1", "VIC1"}
_aemoApiKey = None

class _BoundedRetry(Retry):
    """Prevent Retry-After headers from tying up a polling worker."""

    def get_retry_after(self, response):
        delay = super().get_retry_after(response)
        return min(delay, AEMO_MAX_RETRY_DELAY) if delay is not None else None


# Setup a session with retries
retry_strategy = _BoundedRetry(
    total=AEMO_MAX_RETRIES,
    backoff_factor=AEMO_RETRY_BACKOFF,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http_session = requests.Session()
http_session.mount("https://", adapter)
http_session.mount("http://", adapter)


def aemoResetPriceFirm():
    global aemoPriceFirm    
    aemoPriceFirm = False
    return aemoPriceFirm


class _AemoAuthError(requests.exceptions.RequestException):
    """The dashboard rejected its published API key."""


def _getDashboardJson(url, apiKey=None):
    headers = {"accept": "application/json"}
    if apiKey is not None:
        headers["x-api-key"] = apiKey
    response = http_session.get(url, headers=headers, timeout=30)
    if response.status_code in (401, 403):
        raise _AemoAuthError(f"Dashboard authentication failed (HTTP {response.status_code})")
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise requests.exceptions.RequestException("Dashboard returned a non-object response")
    errors = payload.get("errors", [])
    if not isinstance(errors, list):
        raise requests.exceptions.RequestException("Dashboard returned invalid API errors")
    if errors:
        if any(
            isinstance(error, dict) and str(error.get("code")) in ("401", "403")
            for error in errors
        ):
            raise _AemoAuthError("Dashboard authentication failed")
        raise requests.exceptions.RequestException(f"Dashboard API errors: {errors}")
    if "error" in payload:
        raise requests.exceptions.RequestException(f"Dashboard API error: {payload['error']}")
    return payload


def _loadAemoApiKey():
    global _aemoApiKey
    key = _getDashboardJson(AEMO_CONFIG_URI).get("xApiKey")
    if not isinstance(key, str) or not key.strip():
        raise requests.exceptions.RequestException("Dashboard configuration is missing xApiKey")
    _aemoApiKey = key
    return key


def _aemoSettlementDate(value):
    try:
        settlement = datetime.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise requests.exceptions.RequestException(f"Invalid settlement timestamp: {value!r}") from error
    if settlement.tzinfo is None:
        return settlement.replace(tzinfo=AEMO_MARKET_TIME)
    return settlement.astimezone(AEMO_MARKET_TIME)


def _requireNumbers(record, fields, context):
    for field in fields:
        value = record[field]
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not isfinite(value)
        ):
            raise requests.exceptions.RequestException(
                f"Invalid {context}: {field} must be a finite number"
            )


def _normalizeAemoSummary(payload):
    data = payload.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("summary"), list) or not data["summary"]:
        raise requests.exceptions.RequestException("Dashboard response is missing summary records")
    fields = {
        "settlementDate", "regionId", "price", "priceStatus", "apcFlag",
        "marketsuspendedFlag", "totalDemand", "netInterchange", "scheduledGeneration",
        "semischeduledGeneration", "interconnectorFlows",
    }
    records = []
    regions = set()
    for item in data["summary"]:
        if not isinstance(item, dict) or not fields.issubset(item):
            raise requests.exceptions.RequestException("Invalid electricity summary: missing fields")
        region = item["regionId"]
        if not isinstance(region, str) or region not in AEMO_REGIONS or region in regions:
            raise requests.exceptions.RequestException("Invalid or duplicate dashboard region ID")
        regions.add(region)
        _requireNumbers(
            item,
            {"price", "totalDemand", "netInterchange", "scheduledGeneration", "semischeduledGeneration"},
            "electricity summary",
        )
        if item["apcFlag"] not in (0, 1) or item["marketsuspendedFlag"] not in (0, 1):
            raise requests.exceptions.RequestException("Invalid electricity summary: unknown market flag")
        if not isinstance(item["priceStatus"], str) or not item["priceStatus"]:
            raise requests.exceptions.RequestException("Invalid electricity summary: missing price status")
        try:
            flows = json.loads(item["interconnectorFlows"])
        except (TypeError, ValueError) as error:
            raise requests.exceptions.RequestException("Invalid interconnector flow JSON") from error
        if not isinstance(flows, list):
            raise requests.exceptions.RequestException("Invalid interconnector flows: expected a list")
        for flow in flows:
            if not isinstance(flow, dict) or not {"name", "value", "exportlimit", "importlimit"}.issubset(flow):
                raise requests.exceptions.RequestException("Invalid interconnector flow: missing fields")
            _requireNumbers(flow, {"value", "exportlimit", "importlimit"}, "interconnector flow")
            if not isinstance(flow["name"], str) or not flow["name"]:
                raise requests.exceptions.RequestException("Invalid interconnector flow name")
        record = {key.upper(): value for key, value in item.items()}
        record["PRICE_STATUS"] = record.pop("PRICESTATUS")
        record["INTERCONNECTORFLOWS"] = flows
        record["SETTLEMENTDATE"] = (
            _aemoSettlementDate(item["settlementDate"]).replace(tzinfo=None).isoformat()
        )
        records.append(record)
    if regions != AEMO_REGIONS:
        raise requests.exceptions.RequestException("Dashboard summary is missing NEM regions")
    return {"ELEC_NEM_SUMMARY": records}


def getAemoCurrentData():
    """Fetch dashboard data while retaining the existing MQTT summary format."""
    global _aemoApiKey
    try:
        key = _aemoApiKey or _loadAemoApiKey()
        for attempt in range(2):
            try:
                payload = _getDashboardJson(AEMO_NEM_SUMMARY_URI, key)
                break
            except _AemoAuthError:
                _aemoApiKey = None
                if attempt:
                    raise
                key = _loadAemoApiKey()
        aemoData = _normalizeAemoSummary(payload)
        print(f"The response of AEMO get aemo_price_firm: {aemoData['ELEC_NEM_SUMMARY'][0]['SETTLEMENTDATE']}\n")
        return aemoData
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"API request failed: {e}") from e


def checkAemoSettlementDate(settlementData):
    """Check if the settlement date is current and the price is firm"""
    settlementDate = _aemoSettlementDate(settlementData["SETTLEMENTDATE"])
    timeNow = datetime.now(AEMO_MARKET_TIME)
    if settlementDate - timedelta(minutes=5) <= timeNow < settlementDate:
        print("Settlement Date is current")
        return settlementData["PRICE_STATUS"] == "FIRM"
    return False


def testAemoUnit():
    """Test the AEMO module"""
    global aemoPriceFirm
    test = getAemoCurrentData()
    aemoPriceFirm = checkAemoSettlementDate(test["ELEC_NEM_SUMMARY"][0]) #["SETTLEMENTDATE"])
    print(aemoPriceFirm)
    if aemoPriceFirm:
        print("Price is firm")
    print(test)
    return test

#testAemo = testAemoUnit()
#print(testAemo)