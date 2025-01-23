
AMBER_MQTT_PREFIX = "ambermqtt"
AMBER_DEVICE_ID = "amber2mqtt"
AMBER_DEVICE_NAME = "Amber 2 MQTT"
AMBER_DEVICE_MODEL = "Amber 2 MQTT"
AEMO_DEVICE_ID = "aemo2mqtt"
AEMO_DEVICE_NAME = "AEMO 2 MQTT"
AEMO_DEVICE_MODEL = "AEMO NEM 2 MQTT"

DEVICE_MANUFACTURER = "Skynet"
DEVICE_SW_VERSION = "1.0"
AMBER_OBJECT_NAME = "Amber 5min Price Data"
AMBER_OBJECT_VERSION = "1.0"
AEMO_OBJECT_NAME = "AEMO NEM 5min Price Data"
AEMO_OBJECT_VERSION = "1.0"

OBJECT_URL = "https://github.com/cabberley/amber2mqtt"

HOME_ASSISTANT_DISCOVERY_TOPIC = "homeassistant/device/"
AMBER_DISCOVERY_TOPIC = HOME_ASSISTANT_DISCOVERY_TOPIC + f"{AMBER_DEVICE_ID}/config"
AMBER_STATE_TOPIC_CURRENT = f"{AMBER_MQTT_PREFIX}/state"
AMBER_STATE_TOPIC_PERIODS = f"{AMBER_MQTT_PREFIX}/periods/state"
AEMO_DISCOVERY_TOPIC = HOME_ASSISTANT_DISCOVERY_TOPIC + f"{AEMO_DEVICE_ID}/config"
AEMO_STATE_TOPIC_CURRENT = f"{AMBER_MQTT_PREFIX}/aemo/state"
AEMO_STATE_TOPIC_PERIODS = f"{AMBER_MQTT_PREFIX}/aemo/periods/state"

AMBER_5MIN_CURRENT_GENERAL_ENTITY = "Amber 5min Current General Price"
AMBER_5MIN_CURRENT_FEED_IN_ENTITY = "Amber 5min Current Feed In Price"
AMBER_5MIN_CURRENT_AEMO_ENTITY = "Amber 5min Current AEMO Spot"
AMBER_5MIN_CURRENT_SPIKE_ENTITY = "Amber 5min Current Spike"
AMBER_5MIN_CURRENT_PERIOD_TIME_ENTITY = "Amber 5min Current Period Time"
AMBER_5MIN_LAST_UPDATE = "Amber 5min Current Last Updated"
AMBER_5MIN_CURRENT_GENERAL_DESCRIPTOR_ENTITY = "Amber 5min Current General Descriptor"
AMBER_5MIN_CURRENT_FEED_IN_DESCRIPTOR_ENTITY = "Amber 5min Current Feed In Descriptor"

AEMO_NEM_SUMMARY_URI = "https://visualisations.aemo.com.au/aemo/apps/api/report/ELEC_NEM_SUMMARY"


AEMO_5MIN_CURRENT_PRICE_NSW = "AEMO 5min Current Price NSW"
AEMO_5MIN_CURRENT_PRICE_QLD = "AEMO 5min Current Price QLD"
AEMO_5MIN_CURRENT_PRICE_SA = "AEMO 5min Current Price SA"
AEMO_5MIN_CURRENT_PRICE_TAS = "AEMO 5min Current Price TAS"
AEMO_5MIN_CURRENT_PRICE_VIC = "AEMO 5min Current Price VIC"
AEMO_5MIN_LAST_UPDATE = "AEMO 5min Last Updated"

SENSOR_LIST_AEMO_CURRENT = [
    AEMO_5MIN_CURRENT_PRICE_NSW,
    AEMO_5MIN_CURRENT_PRICE_QLD,
    AEMO_5MIN_CURRENT_PRICE_SA,
    AEMO_5MIN_CURRENT_PRICE_TAS,
    AEMO_5MIN_CURRENT_PRICE_VIC,
]


SENSOR_LIST2 = []

SENSOR_LIST_CURRENT = [
    AMBER_5MIN_CURRENT_GENERAL_ENTITY,
    AMBER_5MIN_CURRENT_FEED_IN_ENTITY,
    AMBER_5MIN_CURRENT_AEMO_ENTITY,
    AMBER_5MIN_LAST_UPDATE,
    
]

SENSOR_LIST = [
    AMBER_5MIN_CURRENT_GENERAL_ENTITY,
    AMBER_5MIN_CURRENT_FEED_IN_ENTITY,
    AMBER_5MIN_CURRENT_AEMO_ENTITY,
]
x=1
while x <= 12:
    SENSOR_LIST.append(f"Amber 5min Period {x} General Price")
    SENSOR_LIST.append(f"Amber 5min Period {x} Feed In Price")
    SENSOR_LIST.append(f"Amber 5min Period {x} AEMO Spot Price")
    x+=1

AMBER_DEVICE = {
        "identifiers": AMBER_DEVICE_ID,
        "name": AMBER_DEVICE_NAME,
        "model": AMBER_DEVICE_MODEL,
        "manufacturer": DEVICE_MANUFACTURER,
        "sw_version": DEVICE_SW_VERSION,
    }

AMBER_OBJECT = {
    "name":AMBER_OBJECT_NAME,
    "sw": AMBER_OBJECT_VERSION,
    "url": OBJECT_URL,
  }

AEMO_DEVICE = {
        "identifiers": AEMO_DEVICE_ID,
        "name": AEMO_DEVICE_NAME,
        "model": AEMO_DEVICE_MODEL,
        "manufacturer": DEVICE_MANUFACTURER,
        "sw_version": DEVICE_SW_VERSION,
    }

AEMO_OBJECT = {
    "name":AEMO_OBJECT_NAME,
    "sw": AEMO_OBJECT_VERSION,
    "url": OBJECT_URL,
  }
