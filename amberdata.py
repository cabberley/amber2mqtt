from __future__ import annotations
from typing import Any
import amberelectric
import amberelectric.models
import amberelectric.api_client
from amberelectric.rest import ApiException
from urllib3.exceptions import HTTPError
import time
import utils as ut
from datetime import timezone, timedelta

AMBER_MAX_RETRIES = 3
AMBER_RETRY_DELAY = 5
AMBER_REQUEST_TIMEOUT = 30


def getAmberData(accessToken, site_id, nextrecords, previous, resolution):
    """Get the current prices from the Amber API"""
    configuration = amberelectric.Configuration(
        access_token = accessToken
    )
    configuration.retries = 0
    
    intervals = None
    for attempt in range(AMBER_MAX_RETRIES):
        # Enter a context with an instance of the API client on each attempt
        # to ensure the client is fresh and properly closed.
        try:
            with amberelectric.ApiClient(configuration) as apiClient:
                apiInstance = amberelectric.AmberApi(apiClient)
                if resolution == 0:
                    data = apiInstance.get_current_prices(
                        site_id, next=nextrecords, previous=previous,
                        _request_timeout=AMBER_REQUEST_TIMEOUT,
                    )
                else:
                    data = apiInstance.get_current_prices(
                        site_id, next=nextrecords, previous=previous, resolution=resolution,
                        _request_timeout=AMBER_REQUEST_TIMEOUT,
                    )
                intervals = [interval.actual_instance for interval in data]
                print("The response of AmberApi->get_current_prices: Success\n")
                # Break on success
                break
        except (ApiException, HTTPError) as e:
            if attempt < AMBER_MAX_RETRIES - 1:
                print(f"Exception when calling AmberApi->get_current_prices (attempt {attempt + 1}): {e}. Retrying in {AMBER_RETRY_DELAY}s...")
                time.sleep(AMBER_RETRY_DELAY)
            else:
                print(f"Final exception when calling AmberApi->get_current_prices: {e}\n")
                raise

    if intervals is None:
        raise RuntimeError("Failed to fetch Amber intervals after retries")

    result: dict[str, dict[str, Any]] = {
            "current": {},
            "descriptors": {},
            "forecasts": {},
            "actuals": {},
            "grid": {},
        }

    current = [interval for interval in intervals if ut.is_current(interval)]
    actuals = [interval for interval in intervals if ut.is_actual(interval)]
    if resolution == 5:
        forecasts = [interval for interval in intervals if ut.is_forecast(interval) and interval.duration == 5]
        general = [interval for interval in current if ut.is_general(interval) and interval.duration == 5]
        feedIn = [interval for interval in current if ut.is_feed_in(interval) and interval.duration == 5]
    else:
        forecasts = [interval for interval in intervals if ut.is_forecast(interval)]
        general = [interval for interval in current if ut.is_general(interval)]
        feedIn = [interval for interval in current if ut.is_feed_in(interval)]

    result["current"]["general"] = general[0]
    result["descriptors"]["general"] = ut.normalize_descriptor(general[0].descriptor)
    result["forecasts"]["general"] = [
        interval for interval in forecasts if ut.is_general(interval)
    ]
    result["actuals"]["general"] = [
        interval for interval in actuals if ut.is_general(interval)
    ]
    result["grid"]["renewables"] = round(general[0].renewables)
    result["grid"]["price_spike"] = general[0].spike_status.value
    tariffInformation = general[0].tariff_information
    if tariffInformation:
        result["grid"]["demand_window"] = tariffInformation.demand_window

    controlledLoad = [
        interval for interval in current if ut.is_controlled_load(interval)
    ]
    if controlledLoad:
        result["current"]["controlled_load"] = controlledLoad[0]
        result["descriptors"]["controlled_load"] = ut.normalize_descriptor(
            controlledLoad[0].descriptor
        )
        result["forecasts"]["controlled_load"] = [
            interval for interval in forecasts if ut.is_controlled_load(interval)
        ]

    feedIn = [interval for interval in current if ut.is_feed_in(interval)]
    if feedIn:
        result["current"]["feed_in"] = feedIn[0]
        result["descriptors"]["feed_in"] = ut.normalize_descriptor(
            feedIn[0].descriptor
        )
        result["forecasts"]["feed_in"] = [
            interval for interval in forecasts if ut.is_feed_in(interval)
        ]
        result["actuals"]["feed_in"] = [
            interval for interval in actuals if ut.is_feed_in(interval)
        ]

    return result

def create_288_5min_intervals(amberData5, amberData30):
    """Create 288 5 minute intervals"""

    result: dict[str, dict[str, Any]] = {
        "forecasts": {},
    }
    result["forecasts"]["general"] = [
        interval for interval in amberData5["forecasts"]["general"]
        ]
    if "feed_in" in amberData5["forecasts"].keys():
        result["forecasts"]["feed_in"] = [
            interval for interval in amberData5["forecasts"]["feed_in"]
            ]
    timeCheckEnd = amberData5["forecasts"]["general"][len(amberData5["forecasts"]["general"])-1].end_time
    for interval in amberData30["forecasts"]["general"]:
        startTime = interval.start_time
        nemTime = interval.nem_time
        for i in range(0, 30, 5):
            newInterval = amberelectric.models.ForecastInterval(
                    type=interval.type,
                    duration=5,
                    spot_per_kwh=interval.spot_per_kwh,
                    per_kwh=interval.per_kwh,
                    var_date=interval.var_date,
                    start_time=startTime + timedelta(minutes=i),
                    end_time=startTime + timedelta(minutes=i+5) - timedelta(seconds=1),
                    nem_time=nemTime - timedelta(seconds=(nemTime-(startTime + timedelta(minutes=i))).seconds) + timedelta(minutes=5) - timedelta(seconds=1),     #.replace(minute=((startTime+timedelta(minutes=i+5)).minute)),
                    renewables=interval.renewables,
                    channel_type=interval.channel_type,
                    tariff_information=interval.tariff_information,
                    spike_status=interval.spike_status,
                    descriptor=interval.descriptor,
                    range=interval.range,
                    advanced_price=interval.advanced_price,
                )
            if newInterval.end_time > timeCheckEnd:
                result["forecasts"]["general"].append(newInterval)
    if len(result["forecasts"]["general"]) > 288:
        result["forecasts"]["general"] = result["forecasts"]["general"][0:288]
    if "feed_in" in amberData30["forecasts"].keys():
        for interval in amberData30["forecasts"]["feed_in"]:
            startTime = interval.start_time
            nemTime = interval.nem_time
            for i in range(0, 30, 5):
                newInterval = amberelectric.models.ForecastInterval(
                        type=interval.type,
                        duration=5,
                        spot_per_kwh=interval.spot_per_kwh,
                        per_kwh=interval.per_kwh,
                        var_date=interval.var_date,
                        start_time=startTime + timedelta(minutes=i),
                        end_time=startTime + timedelta(minutes=i+5) - timedelta(seconds=1),
                        nem_time=nemTime - timedelta(seconds=(nemTime-(startTime + timedelta(minutes=i))).seconds) + timedelta(minutes=5) - timedelta(seconds=1),
                        renewables=interval.renewables,
                        channel_type=interval.channel_type,
                        tariff_information=interval.tariff_information,
                        spike_status=interval.spike_status,
                        descriptor=interval.descriptor,
                        range=interval.range,
                        advanced_price=interval.advanced_price,
                    )
                if newInterval.end_time > timeCheckEnd:
                #not in result["forecasts"]["general"]:
                    result["forecasts"]["feed_in"].append(newInterval)

            if len(result["forecasts"]["feed_in"]) > 288:
                result["forecasts"]["feed_in"] = result["forecasts"]["feed_in"][0:288]
    return result
