from __future__ import annotations
from typing import Any
import amberelectric
from amberelectric.rest import ApiException
import utils as ut


def get_amber_data(access_token, site_id, next, previous, resolution):

    configuration = amberelectric.Configuration(
    host = "https://api.amber.com.au/v1"
    )
    # Configure Bearer authorization: apiKey
    configuration = amberelectric.Configuration(
        access_token = access_token
    )
    # Enter a context with an instance of the API client
    with amberelectric.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = amberelectric.AmberApi(api_client)

        try:
            data = api_instance.get_current_prices(site_id, next=next, previous=previous, resolution=resolution)
            intervals = [interval.actual_instance for interval in data]
            print("The response of AmberApi->get_current_prices:\n")
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
        feed_in = [interval for interval in current if ut.is_feed_in(interval)]

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
        tariff_information = general[0].tariff_information
        if tariff_information:
            result["grid"]["demand_window"] = tariff_information.demand_window

        controlled_load = [
            interval for interval in current if ut.is_controlled_load(interval)
        ]
        if controlled_load:
            result["current"]["controlled_load"] = controlled_load[0]
            result["descriptors"]["controlled_load"] = ut.normalize_descriptor(
                controlled_load[0].descriptor
            )
            result["forecasts"]["controlled_load"] = [
                interval for interval in forecasts if ut.is_controlled_load(interval)
            ]

        feed_in = [interval for interval in current if ut.is_feed_in(interval)]
        if feed_in:
            result["current"]["feed_in"] = feed_in[0]
            result["descriptors"]["feed_in"] = ut.normalize_descriptor(
                feed_in[0].descriptor
            )
            result["forecasts"]["feed_in"] = [
                interval for interval in forecasts if ut.is_feed_in(interval)
            ]
            result["actuals"]["feed_in"] = [
                interval for interval in actuals if ut.is_feed_in(interval)
            ]

    return result
