# Python Modules
from datetime import datetime
import json
import requests
import utils as ut

with open("./config/config.json", "rt", encoding="utf-8") as f:
    config = json.load(f)

amber_5min_general_price_entity = config["home_assistant"]["amber_5min_general_price_entity"]
amber_5min_feedin_price_entity = config["home_assistant"]["amber_5min_feedin_price_entity"]
amber_5min_spike_alert_entity = config["home_assistant"]["amber_5min_spike_alert_entity"]
amber_5min_feedin_slot = config["home_assistant"]["amber_5min_feedin_price_slots"]
amber_5min_general_slot = config["home_assistant"]["amber_5min_general_price_slots"]
hass_url = config["home_assistant"]["url"]
hass_access_token = config["home_assistant"]["access_token"]

headers = {
        "Authorization": f"Bearer {hass_access_token}",
        "Content-Type": "application/json",
    }


def post5MinPrice(amber_data):
    # Load environment variables

    data = {
        "state": ut.format_cents_to_dollars(amber_data["current"]["general"].per_kwh),
        "attributes": {
            "unit_of_measurement": "c/kWh",
            "unique_id": "amber_5min_general_price_entity2",
            "friendly_name": "Amber Current 5min General Price",
            "start_time": amber_data["current"]["general"].start_time.isoformat(),
            "end_time": amber_data["current"]["general"].end_time.isoformat(),
            "nem_time": amber_data["current"]["general"].nem_time.isoformat(),
            "estimate": amber_data["current"]["general"].estimate,
            "duration": amber_data["current"]["general"].duration,
            "update_time": datetime.now().isoformat()
        },
    }
    
    # Set the URL for the Home Assistant API 
    apiUrl = f"{hass_url}/api/states/{amber_5min_general_price_entity}"
    
     # Send the API request to update the sensor state
    try:
        response = requests.post(apiUrl, headers=headers, json=data, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Home Assistant API request failed: {e}") from e
    
    data = {
        "state": ut.format_cents_to_dollars(amber_data["current"]["feed_in"].per_kwh * -1),
        "attributes": {
            "unit_of_measurement": "c/kWh",
            "unique_id": "amber_5min_feedin_price_entity2",
            "friendly_name": "Amber Current 5min Feedin Price",
            "start_time": amber_data["current"]["feed_in"].start_time.isoformat(),
            "end_time": amber_data["current"]["feed_in"].end_time.isoformat(),
            "nem_time": amber_data["current"]["feed_in"].nem_time.isoformat(),
            "estimate": amber_data["current"]["feed_in"].estimate,
            "duration": amber_data["current"]["feed_in"].duration,
            "update_time": datetime.now().isoformat()
        },
    }
    apiUrl = f"{hass_url}/api/states/{amber_5min_feedin_price_entity}"
    
     # Send the API request to update the sensor state
    try:
        response = requests.post(apiUrl, headers=headers, json=data, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Home Assistant API request failed: {e}") from e
    return

def post5minPeriods(amber_data):
    current_period_start = amber_data["current"]["general"].start_time.minute
    slot_general = []
    slot_feedin = []
    if current_period_start < 30:
        current_slot = int(current_period_start / 5)
    else:
        current_slot = int((current_period_start - 30) / 5)
    x = 0
    rows = len(amber_data["actuals"]["general"]) #-1
    while x<current_slot:
        slot_general.append(amber_data["actuals"]["general"][rows - current_slot + x])
        slot_feedin.append(amber_data["actuals"]["feed_in"][rows - current_slot + x])
        x += 1
    slot_general.append(amber_data["current"]["general"])
    slot_feedin.append(amber_data["current"]["feed_in"])
    rows = len(amber_data["forecasts"]["general"])
    while x < 11:
        if x - current_slot <= rows:
            slot_general.append(amber_data["forecasts"]["general"][x - current_slot])
            slot_feedin.append(amber_data["forecasts"]["feed_in"][x - current_slot])
        x += 1
    #print("Slot General: ", slot_general)
    x = 0
    for slot in slot_general:
        data = {
            "state": ut.format_cents_to_dollars(slot.per_kwh),
            "attributes": {
                "unit_of_measurement": "c/kWh",
                "friendly_name": "Amber Current 5min General Price",
                "start_time": slot.start_time.isoformat(),
                "end_time": slot.end_time.isoformat(),
                "nem_time": slot.nem_time.isoformat(),
                "estimate": slot.estimate if ut.is_current(slot) else "Not Applicable",
                "duration": slot.duration,
                "update_time": datetime.now().isoformat()
            },
        }
        apiUrl = f"{hass_url}/api/states/{amber_5min_general_slot}{x}"
        try:
            response = requests.post(apiUrl, headers=headers, json=data, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Home Assistant API request failed: {e}") from e
        x += 1
    x = 0
    for slot in slot_feedin:
        data = {
            "state": ut.format_cents_to_dollars(slot.per_kwh * -1),
            "attributes": {
                "unit_of_measurement": "c/kWh",
                "friendly_name": "Amber Current 5min Feedin Price",
                "start_time": slot.start_time.isoformat(),
                "end_time": slot.end_time.isoformat(),
                "nem_time": slot.nem_time.isoformat(),
                "estimate": slot.estimate if ut.is_current(slot) else "Not Applicable",
                "duration": slot.duration,
                "update_time": datetime.now().isoformat()
            },
        }
        apiUrl = f"{hass_url}/api/states/{amber_5min_feedin_slot}{x}"
        try:
            response = requests.post(apiUrl, headers=headers, json=data, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Home Assistant API request failed: {e}") from e
        x += 1
    return