
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
    AMBER_5MIN_CURRENT_PERIOD_TIME_ENTITY,
    AMBER_5MIN_CURRENT_FEED_IN_DESCRIPTOR_ENTITY,\
    AMBER_5MIN_CURRENT_GENERAL_DESCRIPTOR_ENTITY,
    AEMO_STATE_TOPIC_CURRENT,
    AEMO_STATE_TOPIC_PERIODS,
    SENSOR_LIST_AEMO_CURRENT,
    AEMO_5MIN_CURRENT_PRICE_NSW,
    AEMO_5MIN_CURRENT_PRICE_QLD,
    AEMO_5MIN_CURRENT_PRICE_SA,
    AEMO_5MIN_CURRENT_PRICE_TAS,
    AEMO_5MIN_CURRENT_PRICE_VIC,
)

def ha_discovery_message(): #entity_id):
    cmps = {}
    for sensor in SENSOR_LIST:
        if "Period" in sensor:
            state_topic = AMBER_STATE_TOPIC_PERIODS
        else:
            state_topic = AMBER_STATE_TOPIC_CURRENT
        sensor_dict = {
            "name": sensor,
            "unique_id": sensor.lower().replace(" ", "_"),
            "obj_id": sensor.lower().replace(" ", "_"),
            "state_topic": state_topic,
            "json_attributes_topic": (
                f"{AMBER_MQTT_PREFIX}/{sensor.lower().replace(" ", "_")}/attributes"),
            "device_class":"monetary",
            "unit_of_measurement":"$/kWh",
            "p": "sensor",
            "value_template": "{{ value_json."+ sensor.lower().replace(" ", "_") +" }}",    
        }
        cmps[sensor]=sensor_dict
    sensor = AMBER_5MIN_CURRENT_SPIKE_ENTITY
    sensor_dict = {
            "name": sensor,
            "unique_id": sensor.lower().replace(" ", "_"),
            "obj_id": sensor.lower().replace(" ", "_"),
            "state_topic": AMBER_STATE_TOPIC_CURRENT,
            "p": "sensor",
            "value_template": "{{ value_json."+ sensor.lower().replace(" ", "_") +" }}",    
        }
    cmps[sensor]=sensor_dict
    sensor = AMBER_5MIN_CURRENT_PERIOD_TIME_ENTITY
    sensor_dict = {
            "name": sensor,
            "unique_id": sensor.lower().replace(" ", "_"),
            "obj_id": sensor.lower().replace(" ", "_"),
            "state_topic": AMBER_STATE_TOPIC_CURRENT,
            "p": "sensor",
            "value_template": "{{ value_json."+ sensor.lower().replace(" ", "_") +" }}",    
        }
    cmps[sensor]=sensor_dict
    sensor = AMBER_5MIN_CURRENT_FEED_IN_DESCRIPTOR_ENTITY
    sensor_dict = {
            "name": sensor,
            "unique_id": sensor.lower().replace(" ", "_"),
            "obj_id": sensor.lower().replace(" ", "_"),
            "state_topic": AMBER_STATE_TOPIC_CURRENT,
            "p": "sensor",
            "value_template": "{{ value_json."+ sensor.lower().replace(" ", "_") +" }}",    
        }
    cmps[sensor]=sensor_dict
    sensor = AMBER_5MIN_CURRENT_GENERAL_DESCRIPTOR_ENTITY
    sensor_dict = {
            "name": sensor,
            "unique_id": sensor.lower().replace(" ", "_"),
            "obj_id": sensor.lower().replace(" ", "_"),
            "state_topic": AMBER_STATE_TOPIC_CURRENT,
            "p": "sensor",
            "value_template": "{{ value_json."+ sensor.lower().replace(" ", "_") +" }}",    
        }
    cmps[sensor]=sensor_dict
    discoveryMsg = {
        "device": AMBER_DEVICE,
        "o": AMBER_OBJECT,
        "cmps": cmps,
    }
    return discoveryMsg

def ha_aemo_discovery_message():
    cmps = {}
    for sensor in SENSOR_LIST_AEMO_CURRENT:
        if "Period" in sensor:
            state_topic = AEMO_STATE_TOPIC_PERIODS
        else:
            state_topic = AEMO_STATE_TOPIC_CURRENT
        sensor_dict = {
            "name": sensor,
            "unique_id": sensor.lower().replace(" ", "_"),
            "obj_id": sensor.lower().replace(" ", "_"),
            "state_topic": state_topic,
            "json_attributes_topic": (
                f"{AMBER_MQTT_PREFIX}/{sensor.lower().replace(" ", "_")}/attributes"),
            "device_class":"monetary",
            "unit_of_measurement":"$/kWh",
            "p": "sensor",
            "value_template": "{{ value_json."+ sensor.lower().replace(" ", "_") +" }}",    
        }
        cmps[sensor]=sensor_dict
    discoveryMsg = {
        "device": AMBER_DEVICE,
        "o": AMBER_OBJECT,
        "cmps": cmps,
    }
    return discoveryMsg

def ha_state_message(amberdata):
    stateMsg = {
        "state": {
            AMBER_5MIN_CURRENT_GENERAL_ENTITY.lower().replace(" ", "_") :
                ut.format_cents_to_dollars(amberdata["current"]["general"].per_kwh),
            AMBER_5MIN_CURRENT_FEED_IN_ENTITY.lower().replace(" ", "_") :
                ut.format_cents_to_dollars(amberdata["current"]["feed_in"].per_kwh * -1),
            AMBER_5MIN_CURRENT_AEMO_ENTITY.lower().replace(" ", "_") :
                ut.format_cents_to_dollars(amberdata["current"]["general"].spot_per_kwh),
            AMBER_5MIN_CURRENT_SPIKE_ENTITY.lower().replace(" ", "_") :
                amberdata["current"]["general"].spike_status, #if amberdata["current"]["general"].spike_status != None else "False",
            AMBER_5MIN_CURRENT_PERIOD_TIME_ENTITY.lower().replace(" ", "_") :
                amberdata["current"]["general"].start_time.isoformat(),
            AMBER_5MIN_CURRENT_GENERAL_DESCRIPTOR_ENTITY.lower().replace(" ", "_") :
                amberdata["current"]["general"].descriptor,
            AMBER_5MIN_CURRENT_FEED_IN_DESCRIPTOR_ENTITY.lower().replace(" ", "_") :
                amberdata["current"]["feed_in"].descriptor,
        },
        "attributes": {
            "start_time": amberdata["current"]["general"].start_time.isoformat(),
            "end_time": amberdata["current"]["general"].end_time.isoformat(),
            "nem_time": amberdata["current"]["general"].nem_time.isoformat(),
            "estimate": amberdata["current"]["general"].estimate,
            "duration": amberdata["current"]["general"].duration,
            "descriptor": amberdata["current"]["general"].descriptor,
            "type": amberdata["current"]["general"].type,
            "spot_per_kwh": 
                ut.format_cents_to_dollars(amberdata["current"]["general"].spot_per_kwh),
            "renewables": amberdata["current"]["general"].renewables,
            "spike_status": amberdata["current"]["general"].spike_status,
            "update_time": datetime.now().isoformat()
        },
    }
    return stateMsg

def ha_state_5minPeriods(amberdata):
    stateMsg = {}
    attributes = {}
    current_period_start = amberdata["current"]["general"].start_time.minute
    slot_general = []
    slot_feedin = []
    slot_aemo = []
    if current_period_start < 30:
        current_slot = int(current_period_start / 5)
    else:
        current_slot = int((current_period_start - 30) / 5)
    x = 0
    rows = len(amberdata["actuals"]["general"]) #-1
    while x<current_slot:
        slot_general.append(amberdata["actuals"]["general"][rows - current_slot + x])
        slot_aemo.append(amberdata["actuals"]["general"][rows - current_slot + x])
        slot_feedin.append(amberdata["actuals"]["feed_in"][rows - current_slot + x])
        x += 1
    slot_general.append(amberdata["current"]["general"])
    slot_feedin.append(amberdata["current"]["feed_in"])
    rows = len(amberdata["forecasts"]["general"])
    while x < 11:
        if x - current_slot <= rows:
            slot_general.append(amberdata["forecasts"]["general"][x - current_slot])
            slot_aemo.append(amberdata["forecasts"]["general"][x - current_slot])
            slot_feedin.append(amberdata["forecasts"]["feed_in"][x - current_slot])
        x += 1
    #print("Slot General: ", slot_general)
    x = 1
    data = {}
    for slot in slot_general:
        data[f"amber_5min_period_{x}_general_price"] = ut.format_cents_to_dollars(slot.per_kwh)
        attributes[f"amber_5min_period_{x}_general_price"] = {
            "start_time": slot.start_time.isoformat(),
            "end_time": slot.end_time.isoformat(),
            "nem_time": slot.nem_time.isoformat(),
            "estimate": True,
            "duration": slot.duration,
            "descriptor": slot.descriptor,
            "type": slot.type,
            "spot_per_kwh": 
                ut.format_cents_to_dollars(slot.spot_per_kwh),
            "renewables": slot.renewables,
            "spike_status": slot.spike_status,
            "update_time": datetime.now().isoformat()
        }
        #if ut.is_current(slot):
        #    attributes[f"amber_5min_period_{x}_general_price"]["estimate"] = slot.estimate
        #if ut.is_current(slot) or ut.is_forecast(slot): #and not slot.estimate:
        #    attributes[f"amber_5min_period_{x}_general_price"]["advanced_price"] = slot.advanced_price
        data[f"amber_5min_period_{x}_aemo_spot_price"] = ut.format_cents_to_dollars(slot.spot_per_kwh)
        attributes[f"amber_5min_period_{x}_aemo_spot_price"] = {
            "start_time": slot.start_time.isoformat(),
            "end_time": slot.end_time.isoformat(),
            "nem_time": slot.nem_time.isoformat(),
            "estimate": True,
            "duration": slot.duration,
            "descriptor": slot.descriptor,
            "type": slot.type,
            "spot_per_kwh": 
                ut.format_cents_to_dollars(slot.spot_per_kwh),
            "renewables": slot.renewables,
            "spike_status": slot.spike_status,
            "update_time": datetime.now().isoformat()
        }
        if ut.is_current(slot):
            attributes[f"amber_5min_period_{x}_aemo_spot_price"]["estimate"] = slot.estimate
            attributes[f"amber_5min_period_{x}_general_price"]["estimate"] = slot.estimate
        #if "advanced_price" in slot.keys():
        if ut.is_current(slot) and not slot.estimate or ut.is_forecast(slot):
            if slot.advanced_price != None:
                attributes[f"amber_5min_period_{x}_general_price"]["advanced_price_low"] = ut.format_cents_to_dollars(slot.advanced_price.low)
                attributes[f"amber_5min_period_{x}_general_price"]["advanced_price_predicted"] = ut.format_cents_to_dollars(slot.advanced_price.predicted)
                attributes[f"amber_5min_period_{x}_general_price"]["advanced_price_high"] = ut.format_cents_to_dollars(slot.advanced_price.high)
        x += 1
    x = 1
    for slot in slot_feedin:
        data[f"amber_5min_period_{x}_feed_in_price"] = ut.format_cents_to_dollars(slot.per_kwh * -1)
        attributes[f"amber_5min_period_{x}_feed_in_price"] = {
            "start_time": slot.start_time.isoformat(),
            "end_time": slot.end_time.isoformat(),
            "nem_time": slot.nem_time.isoformat(),
            "estimate": True,
            "duration": slot.duration,
            "descriptor": slot.descriptor,
            "type": slot.type,
            "spot_per_kwh": 
                ut.format_cents_to_dollars(slot.spot_per_kwh),
            "renewables": slot.renewables,
            "spike_status": slot.spike_status,
            "update_time": datetime.now().isoformat()
        }
        if ut.is_current(slot):
            attributes[f"amber_5min_period_{x}_feed_in_price"]["estimate"] = slot.estimate
        if ut.is_current(slot) and not slot.estimate or ut.is_forecast(slot):
            if slot.advanced_price != None:
                attributes[f"amber_5min_period_{x}_feed_in_price"]["advanced_price_low"] = ut.format_cents_to_dollars(slot.advanced_price.low)
                attributes[f"amber_5min_period_{x}_feed_in_price"]["advanced_price_predicted"] = ut.format_cents_to_dollars(slot.advanced_price.predicted)
                attributes[f"amber_5min_period_{x}_feed_in_price"]["advanced_price_high"] = ut.format_cents_to_dollars(slot.advanced_price.high)
        x += 1
    stateMsg = {"state": data, "attributes": attributes}
    return stateMsg

def ha_aemo_state_attributes_add(regiondata):
    attributes = {}
    #attributes[region.lower().replace(" ", "_")] = {
    attributes = {
                "settlement_date": regiondata["SETTLEMENTDATE"],
                #"settlement_date_time": datetime.strptime(regiondata["SETTLEMENTDATE"], "%Y-%m-%dT%H:%M:%S"),
                "price_status": regiondata["PRICE_STATUS"],
                "apc_flag": regiondata["APCFLAG"],
                "market_suspended": regiondata["MARKETSUSPENDEDFLAG"],
                "total_demand": regiondata["TOTALDEMAND"],
                "net_interchange": regiondata["NETINTERCHANGE"],
                "scheduled_generation": regiondata["SCHEDULEDGENERATION"],
                "semi_scheduled_generation": regiondata["SEMISCHEDULEDGENERATION"],
                "update_time": datetime.now().isoformat(),
                #"interconnector_flows": None,
            }
    #interconnector_flows = {}
    if regiondata["INTERCONNECTORFLOWS"] != None:
        for connector in regiondata["INTERCONNECTORFLOWS"]:
            attributes[F"interconnector_flows_{connector['name']}"] = {
            #interconnector_flows[connector["name"]] = {
                "name": connector["name"],
                "value": connector["value"],
                "export_limit": connector["exportlimit"],
                "import_limit": connector["importlimit"],
            }
        #attributes["interconnector_flows"] = interconnector_flows
    return attributes

def ha_aemo_current_state_message(aemodata):
    state = {}
    attributes = {}
    stateMsg = {}
    for region in aemodata["ELEC_NEM_SUMMARY"]:
        if region["REGIONID"] == "NSW1":
            state[AEMO_5MIN_CURRENT_PRICE_NSW.lower().replace(" ", "_")] = round(region["PRICE"]/1000, 4)
            attributes[AEMO_5MIN_CURRENT_PRICE_NSW.lower().replace(" ", "_")] = ha_aemo_state_attributes_add(region)
        elif region["REGIONID"] == "QLD1":
            state[AEMO_5MIN_CURRENT_PRICE_QLD.lower().replace(" ", "_")] = round(region["PRICE"]/1000, 4)
            attributes[AEMO_5MIN_CURRENT_PRICE_QLD.lower().replace(" ", "_")] = ha_aemo_state_attributes_add(region)
        elif region["REGIONID"] == "SA1":
            state[AEMO_5MIN_CURRENT_PRICE_SA.lower().replace(" ", "_")] = round(region["PRICE"]/1000, 4)
            attributes[AEMO_5MIN_CURRENT_PRICE_SA.lower().replace(" ", "_")] = ha_aemo_state_attributes_add(region)
        elif region["REGIONID"] == "TAS1":
            state[AEMO_5MIN_CURRENT_PRICE_TAS.lower().replace(" ", "_")] = round(region["PRICE"]/1000, 4)
            attributes[AEMO_5MIN_CURRENT_PRICE_TAS.lower().replace(" ", "_")] = ha_aemo_state_attributes_add(region)
        elif region["REGIONID"] == "VIC1":
            state[AEMO_5MIN_CURRENT_PRICE_VIC.lower().replace(" ", "_")] = round(region["PRICE"]/1000, 4)
            attributes[AEMO_5MIN_CURRENT_PRICE_VIC.lower().replace(" ", "_")] = ha_aemo_state_attributes_add(region)
    stateMsg = {"state": state, "attributes": attributes}
    return stateMsg
