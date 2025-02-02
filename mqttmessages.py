"""Create the MQTT messages for the Amber and AEMO data"""
import utils as ut
from datetime import datetime

from const import (
    SENSOR_LIST,
    AMBER_DEVICE,
    AMBER_OBJECT,
    AMBER_MQTT_PREFIX,
    AMBER_STATE_TOPIC_CURRENT,
    AMBER_STATE_TOPIC_PERIODS,
    AMBER_5MIN_CURRENT_GENERAL_ENTITY,
    AMBER_5MIN_CURRENT_FEED_IN_ENTITY,
    AMBER_5MIN_CURRENT_AEMO_ENTITY,
    AMBER_5MIN_CURRENT_SPIKE_ENTITY,
    AMBER_5MIN_LAST_UPDATE,
    AMBER_5MIN_CURRENT_PERIOD_TIME_ENTITY,
    AMBER_5MIN_CURRENT_FEED_IN_DESCRIPTOR_ENTITY,
    AMBER_5MIN_CURRENT_GENERAL_DESCRIPTOR_ENTITY,
    AEMO_DEVICE,
    AEMO_OBJECT,
    AEMO_STATE_TOPIC_CURRENT,
    AEMO_STATE_TOPIC_PERIODS,
    SENSOR_LIST_AEMO_CURRENT,
    AEMO_5MIN_CURRENT_PRICE_NSW,
    AEMO_5MIN_CURRENT_PRICE_QLD,
    AEMO_5MIN_CURRENT_PRICE_SA,
    AEMO_5MIN_CURRENT_PRICE_TAS,
    AEMO_5MIN_CURRENT_PRICE_VIC,
    AEMO_5MIN_LAST_UPDATE,
)


def amberDiscoveryMessage():
    """Create the Amber discovery message"""
    cmps = {}
    for sensor in SENSOR_LIST:
        if "Period" in sensor:
            state_topic = AMBER_STATE_TOPIC_PERIODS
        else:
            state_topic = AMBER_STATE_TOPIC_CURRENT
        sensorDict = {
            "name": sensor,
            "unique_id": sensor.lower().replace(" ", "_"),
            "obj_id": sensor.lower().replace(" ", "_"),
            "state_topic": state_topic,
            "json_attributes_topic": (
                f"{AMBER_MQTT_PREFIX}/{sensor.lower().replace(' ', '_')}/attributes"
            ),
            "device_class": "monetary",
            "unit_of_measurement": "$/kWh",
            "p": "sensor",
            "value_template": "{{ value_json."
            + sensor.lower().replace(" ", "_")
            + " }}",
        }
        cmps[sensor] = sensorDict
    sensor = AMBER_5MIN_CURRENT_SPIKE_ENTITY
    sensorDict = {
        "name": sensor,
        "unique_id": sensor.lower().replace(" ", "_"),
        "obj_id": sensor.lower().replace(" ", "_"),
        "state_topic": AMBER_STATE_TOPIC_CURRENT,
        "p": "sensor",
        "value_template": "{{ value_json." + sensor.lower().replace(" ", "_") + " }}",
    }
    cmps[sensor] = sensorDict
    sensor = AMBER_5MIN_CURRENT_PERIOD_TIME_ENTITY
    sensorDict = {
        "name": sensor,
        "unique_id": sensor.lower().replace(" ", "_"),
        "obj_id": sensor.lower().replace(" ", "_"),
        "state_topic": AMBER_STATE_TOPIC_CURRENT,
        "p": "sensor",
        "value_template": "{{ value_json." + sensor.lower().replace(" ", "_") + " }}",
    }
    cmps[sensor] = sensorDict
    sensor = AMBER_5MIN_CURRENT_FEED_IN_DESCRIPTOR_ENTITY
    sensorDict = {
        "name": sensor,
        "unique_id": sensor.lower().replace(" ", "_"),
        "obj_id": sensor.lower().replace(" ", "_"),
        "state_topic": AMBER_STATE_TOPIC_CURRENT,
        "p": "sensor",
        "value_template": "{{ value_json." + sensor.lower().replace(" ", "_") + " }}",
    }
    cmps[sensor] = sensorDict
    sensor = AMBER_5MIN_CURRENT_GENERAL_DESCRIPTOR_ENTITY
    sensorDict = {
        "name": sensor,
        "unique_id": sensor.lower().replace(" ", "_"),
        "obj_id": sensor.lower().replace(" ", "_"),
        "state_topic": AMBER_STATE_TOPIC_CURRENT,
        "p": "sensor",
        "value_template": "{{ value_json." + sensor.lower().replace(" ", "_") + " }}",
    }
    cmps[sensor] = sensorDict
    sensor = AMBER_5MIN_LAST_UPDATE
    sensorDict = {
        "name": sensor,
        "unique_id": sensor.lower().replace(" ", "_"),
        "obj_id": sensor.lower().replace(" ", "_"),
        "state_topic": AMBER_STATE_TOPIC_CURRENT,
        "p": "sensor",
        "value_template": "{{ value_json." + sensor.lower().replace(" ", "_") + " }}",
    }
    cmps[sensor] = sensorDict
    discoveryMsg = {
        "device": AMBER_DEVICE,
        "o": AMBER_OBJECT,
        "cmps": cmps,
    }
    return discoveryMsg


def aemoDiscoveryMessage():
    """Create the AEMO discovery message"""
    cmps = {}
    for sensor in SENSOR_LIST_AEMO_CURRENT:
        if "Period" in sensor:
            state_topic = AEMO_STATE_TOPIC_PERIODS
        else:
            state_topic = AEMO_STATE_TOPIC_CURRENT
        sensorDict = {
            "name": sensor,
            "unique_id": sensor.lower().replace(" ", "_"),
            "obj_id": sensor.lower().replace(" ", "_"),
            "state_topic": state_topic,
            "json_attributes_topic": (
                f"{AMBER_MQTT_PREFIX}/{sensor.lower().replace(' ', '_')}/attributes"
            ),
            "device_class": "monetary",
            "unit_of_measurement": "$/kWh",
            "p": "sensor",
            "value_template": "{{ value_json."
            + sensor.lower().replace(" ", "_")
            + " }}",
        }
        cmps[sensor] = sensorDict
    sensor = AEMO_5MIN_LAST_UPDATE
    sensorDict = {
        "name": sensor,
        "unique_id": sensor.lower().replace(" ", "_"),
        "obj_id": sensor.lower().replace(" ", "_"),
        "state_topic": AEMO_STATE_TOPIC_CURRENT,
        "p": "sensor",
        "value_template": "{{ value_json." + sensor.lower().replace(" ", "_") + " }}",
    }
    cmps[sensor] = sensorDict
    discoveryMsg = {
        "device": AEMO_DEVICE,
        "o": AEMO_OBJECT,
        "cmps": cmps,
    }
    return discoveryMsg


def amberStateMessage(amberdata):
    """Publish the current Amber state to MQTT"""
    stateMsg = {
        "state": {
            AMBER_5MIN_CURRENT_GENERAL_ENTITY.lower().replace(
                " ", "_"
            ): ut.format_cents_to_dollars(amberdata["current"]["general"].per_kwh),
            AMBER_5MIN_CURRENT_FEED_IN_ENTITY.lower().replace(
                " ", "_"
            ): ut.format_cents_to_dollars(amberdata["current"]["feed_in"].per_kwh * -1),
            AMBER_5MIN_CURRENT_AEMO_ENTITY.lower().replace(
                " ", "_"
            ): ut.format_cents_to_dollars(amberdata["current"]["general"].spot_per_kwh),
            AMBER_5MIN_CURRENT_SPIKE_ENTITY.lower().replace(" ", "_"): amberdata[
                "current"
            ][
                "general"
            ].spike_status,  # if amberdata["current"]["general"].spike_status != None else "False",
            AMBER_5MIN_CURRENT_PERIOD_TIME_ENTITY.lower().replace(" ", "_"): amberdata[
                "current"
            ]["general"].start_time.isoformat(),
            AMBER_5MIN_CURRENT_GENERAL_DESCRIPTOR_ENTITY.lower().replace(
                " ", "_"
            ): amberdata["current"]["general"].descriptor,
            AMBER_5MIN_CURRENT_FEED_IN_DESCRIPTOR_ENTITY.lower().replace(
                " ", "_"
            ): amberdata["current"]["feed_in"].descriptor,
            AMBER_5MIN_LAST_UPDATE.lower().replace(" ", "_"): datetime.now().isoformat(),
        },
        "attributes": {
            "start_time": amberdata["current"]["general"].start_time.isoformat(),
            "start_time_time": amberdata["current"]["general"].start_time.time().isoformat(),
            "end_time": amberdata["current"]["general"].end_time.isoformat(),
            "nem_time": amberdata["current"]["general"].nem_time.isoformat(),
            "estimate": amberdata["current"]["general"].estimate,
            "duration": amberdata["current"]["general"].duration,
            "descriptor": amberdata["current"]["general"].descriptor,
            "type": amberdata["current"]["general"].type,
            "spot_per_kwh": ut.format_cents_to_dollars(
                amberdata["current"]["general"].spot_per_kwh
            ),
            "renewables": amberdata["current"]["general"].renewables,
            "spike_status": amberdata["current"]["general"].spike_status,
            "update_time": datetime.now().isoformat(),
        },
    }
    return stateMsg


def amberState5MinPeriods(amberdata):
    """Publish the Amber state to MQTT for the 12 periods"""
    stateMsg = {}
    attributes = {}
    currentPeriodStart = amberdata["current"]["general"].start_time.minute
    slotGeneral = []
    slotFeedin = []
    slotAemo = []
    if currentPeriodStart < 30:
        currentSlot = int(currentPeriodStart / 5)
    else:
        currentSlot = int((currentPeriodStart - 30) / 5)
    x = 0
    rows = len(amberdata["actuals"]["general"])
    while x < currentSlot:
        slotGeneral.append(amberdata["actuals"]["general"][rows - currentSlot + x])
        slotAemo.append(amberdata["actuals"]["general"][rows - currentSlot + x])
        slotFeedin.append(amberdata["actuals"]["feed_in"][rows - currentSlot + x])
        x += 1
    slotGeneral.append(amberdata["current"]["general"])
    slotFeedin.append(amberdata["current"]["feed_in"])
    rows = len(amberdata["forecasts"]["general"])
    while x < 11:
        if x - currentSlot <= rows:
            slotGeneral.append(amberdata["forecasts"]["general"][x - currentSlot])
            slotAemo.append(amberdata["forecasts"]["general"][x - currentSlot])
            slotFeedin.append(amberdata["forecasts"]["feed_in"][x - currentSlot])
        x += 1
    x = 1
    data = {}
    for slot in slotGeneral:
        data[f"amber_5min_period_{x}_general_price"] = ut.format_cents_to_dollars(
            slot.per_kwh
        )
        attributes[f"amber_5min_period_{x}_general_price"] = {
            "start_time": slot.start_time.isoformat(),
            "start_time_time": slot.start_time.time().isoformat(),
            "end_time": slot.end_time.isoformat(),
            "nem_time": slot.nem_time.isoformat(),
            "estimate": True,
            "duration": slot.duration,
            "descriptor": slot.descriptor,
            "type": slot.type,
            "spot_per_kwh": ut.format_cents_to_dollars(slot.spot_per_kwh),
            "renewables": slot.renewables,
            "spike_status": slot.spike_status,
            "update_time": datetime.now().isoformat(),
        }
        data[f"amber_5min_period_{x}_aemo_spot_price"] = ut.format_cents_to_dollars(
            slot.spot_per_kwh
        )
        attributes[f"amber_5min_period_{x}_aemo_spot_price"] = {
            "start_time": slot.start_time.isoformat(),
            "start_time_time": slot.start_time.time().isoformat(),
            "end_time": slot.end_time.isoformat(),
            "nem_time": slot.nem_time.isoformat(),
            "estimate": True,
            "duration": slot.duration,
            "descriptor": slot.descriptor,
            "type": slot.type,
            "spot_per_kwh": ut.format_cents_to_dollars(slot.spot_per_kwh),
            "renewables": slot.renewables,
            "spike_status": slot.spike_status,
            "update_time": datetime.now().isoformat(),
        }
        if ut.is_current(slot):
            attributes[f"amber_5min_period_{x}_aemo_spot_price"]["estimate"] = (
                slot.estimate
            )
            attributes[f"amber_5min_period_{x}_general_price"]["estimate"] = (
                slot.estimate
            )
        # if "advanced_price" in slot.keys():
        if ut.is_current(slot) and not slot.estimate or ut.is_forecast(slot):
            if slot.advanced_price != None:
                attributes[f"amber_5min_period_{x}_general_price"][
                    "advanced_price_low"
                ] = ut.format_cents_to_dollars(slot.advanced_price.low)
                attributes[f"amber_5min_period_{x}_general_price"][
                    "advanced_price_predicted"
                ] = ut.format_cents_to_dollars(slot.advanced_price.predicted)
                attributes[f"amber_5min_period_{x}_general_price"][
                    "advanced_price_high"
                ] = ut.format_cents_to_dollars(slot.advanced_price.high)
        x += 1
    x = 1
    for slot in slotFeedin:
        data[f"amber_5min_period_{x}_feed_in_price"] = ut.format_cents_to_dollars(
            slot.per_kwh * -1
        )
        attributes[f"amber_5min_period_{x}_feed_in_price"] = {
            "start_time": slot.start_time.isoformat(),
            "start_time_time": slot.start_time.time().isoformat(),
            "end_time": slot.end_time.isoformat(),
            "nem_time": slot.nem_time.isoformat(),
            "estimate": True,
            "duration": slot.duration,
            "descriptor": slot.descriptor,
            "type": slot.type,
            "spot_per_kwh": ut.format_cents_to_dollars(slot.spot_per_kwh),
            "renewables": slot.renewables,
            "spike_status": slot.spike_status,
            "update_time": datetime.now().isoformat(),
        }
        if ut.is_current(slot):
            attributes[f"amber_5min_period_{x}_feed_in_price"]["estimate"] = (
                slot.estimate
            )
        if ut.is_current(slot) and not slot.estimate or ut.is_forecast(slot):
            if slot.advanced_price != None:
                attributes[f"amber_5min_period_{x}_feed_in_price"][
                    "advanced_price_low"
                ] = ut.format_cents_to_dollars(slot.advanced_price.low)
                attributes[f"amber_5min_period_{x}_feed_in_price"][
                    "advanced_price_predicted"
                ] = ut.format_cents_to_dollars(slot.advanced_price.predicted)
                attributes[f"amber_5min_period_{x}_feed_in_price"][
                    "advanced_price_high"
                ] = ut.format_cents_to_dollars(slot.advanced_price.high)
        x += 1
    stateMsg = {"state": data, "attributes": attributes}
    return stateMsg


def aemoStateAttributesAdd(regionData):
    attributes = {}
    attributes = {
        "settlement_date": regionData["SETTLEMENTDATE"],
        "price_status": regionData["PRICE_STATUS"],
        "apc_flag": regionData["APCFLAG"],
        "market_suspended": regionData["MARKETSUSPENDEDFLAG"],
        "total_demand": regionData["TOTALDEMAND"],
        "net_interchange": regionData["NETINTERCHANGE"],
        "scheduled_generation": regionData["SCHEDULEDGENERATION"],
        "semi_scheduled_generation": regionData["SEMISCHEDULEDGENERATION"],
        "update_time": datetime.now().isoformat(),
    }
    if regionData["INTERCONNECTORFLOWS"] != None:
        for connector in regionData["INTERCONNECTORFLOWS"]:
            attributes[f"interconnector_flows_{connector['name']}"] = {
                "name": connector["name"],
                "value": connector["value"],
                "export_limit": connector["exportlimit"],
                "import_limit": connector["importlimit"],
            }
    return attributes


def aemoCurrentStateMessage(aemoData):
    state = {}
    attributes = {}
    stateMsg = {}
    state[AEMO_5MIN_LAST_UPDATE.lower().replace(" ", "_")] = datetime.now().isoformat()
    for region in aemoData["ELEC_NEM_SUMMARY"]:
        if region["REGIONID"] == "NSW1":
            state[AEMO_5MIN_CURRENT_PRICE_NSW.lower().replace(" ", "_")] = round(
                region["PRICE"] / 1000, 4
            )
            attributes[AEMO_5MIN_CURRENT_PRICE_NSW.lower().replace(" ", "_")] = (
                aemoStateAttributesAdd(region)
            )
        elif region["REGIONID"] == "QLD1":
            state[AEMO_5MIN_CURRENT_PRICE_QLD.lower().replace(" ", "_")] = round(
                region["PRICE"] / 1000, 4
            )
            attributes[AEMO_5MIN_CURRENT_PRICE_QLD.lower().replace(" ", "_")] = (
                aemoStateAttributesAdd(region)
            )
        elif region["REGIONID"] == "SA1":
            state[AEMO_5MIN_CURRENT_PRICE_SA.lower().replace(" ", "_")] = round(
                region["PRICE"] / 1000, 4
            )
            attributes[AEMO_5MIN_CURRENT_PRICE_SA.lower().replace(" ", "_")] = (
                aemoStateAttributesAdd(region)
            )
        elif region["REGIONID"] == "TAS1":
            state[AEMO_5MIN_CURRENT_PRICE_TAS.lower().replace(" ", "_")] = round(
                region["PRICE"] / 1000, 4
            )
            attributes[AEMO_5MIN_CURRENT_PRICE_TAS.lower().replace(" ", "_")] = (
                aemoStateAttributesAdd(region)
            )
        elif region["REGIONID"] == "VIC1":
            state[AEMO_5MIN_CURRENT_PRICE_VIC.lower().replace(" ", "_")] = round(
                region["PRICE"] / 1000, 4
            )
            attributes[AEMO_5MIN_CURRENT_PRICE_VIC.lower().replace(" ", "_")] = (
                aemoStateAttributesAdd(region)
            )
    stateMsg = {"state": state, "attributes": attributes}
    return stateMsg
