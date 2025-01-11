
AMBER_MQTT_PREFIX = "ambermqtt"
DEVICE_ID = "amber2mqtt"
DEVICE_NAME = "Amber 2 MQTT"
DEVICE_MODEL = "Amber 2 MQTT"
DEVICE_MANUFACTURER = "Chris Abberley"
DEVICE_SW_VERSION = "0.1"
OBJECT_NAME = "Amber 5min Price Data"
OBJECT_VERSION = "1.0"
OBJECT_URL = "https://github.com/cabberley/amber2mqtt"

HOME_ASSISTANT_DISCOVERY_TOPIC = f"homeassistant/device/{DEVICE_ID}/config"
AMBER_STATE_TOPIC_CURRENT = f"{AMBER_MQTT_PREFIX}/state"
AMBER_STATE_TOPIC_PERIODS = f"{AMBER_MQTT_PREFIX}/periods/state"

AMBER_5MIN_CURRENT_GENERAL_ENTITY = "Amber 5min Current General Price"
AMBER_5MIN_CURRENT_FEED_IN_ENTITY = "Amber 5min Current Feed In Price"
AMBER_5MIN_CURRENT_AEMO_ENTITY = "Amber 5min Current AEMO Spot"
AMBER_5MIN_CURRENT_SPIKE_ENTITY = "Amber 5min Current Spike"

SENSOR_LIST2 = []

SENSOR_LIST_CURRENT = [
    AMBER_5MIN_CURRENT_GENERAL_ENTITY,
    AMBER_5MIN_CURRENT_FEED_IN_ENTITY,
    AMBER_5MIN_CURRENT_AEMO_ENTITY,
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
        "identifiers": DEVICE_ID,
        "name": DEVICE_NAME,
        "model": DEVICE_MODEL,
        "manufacturer": DEVICE_MANUFACTURER,
        "sw_version": DEVICE_SW_VERSION,
    }

AMBER_OBJECT = {
    "name":OBJECT_NAME,
    "sw": DEVICE_SW_VERSION,
    "url": OBJECT_URL,
  }

