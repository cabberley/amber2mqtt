from __future__ import annotations
from typing import Any
import amberelectric
import amberelectric.api_client
from amberelectric.rest import ApiException
import utils as ut


def getAmberData(accessToken, site_id, nextrecords, previous, resolution):
    """Get the current prices from the Amber API"""
    configuration = amberelectric.Configuration(
    host = "https://api.amber.com.au/v1"
    )
    # Configure Bearer authorization: apiKey
    configuration = amberelectric.Configuration(
        access_token = accessToken
    )
    # Enter a context with an instance of the API client
    with amberelectric.ApiClient(configuration) as apiClient:
        # Create an instance of the API class
        apiInstance = amberelectric.AmberApi(apiClient)

        try:
            data = apiInstance.get_current_prices(site_id, next=nextrecords, previous=previous, resolution=resolution)
            intervals = [interval.actual_instance for interval in data]
            print("The response of AmberApi->get_current_prices:\n")
            apiInstance.api_client.close()
        except ApiException as e:
            print("Exception when calling AmberApi->get_current_prices: %s\n" % e)

        result: dict[str, dict[str, Any]] = {
                "current": {},
                "descriptors": {},
                "forecasts": {},
                "actuals": {},
                "grid": {},
            }

        current = [interval for interval in intervals if ut.is_current(interval)]
        actuals = [interval for interval in intervals if ut.is_actual(interval)]
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
