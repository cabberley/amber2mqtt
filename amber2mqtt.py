from paho.mqtt import client as mqtt_client
import json
import mqttmessages as mm
from const import (
    HOME_ASSISTANT_DISCOVERY_TOPIC,
    AMBER_STATE_TOPIC_CURRENT,
    AMBER_STATE_TOPIC_PERIODS,
    AMBER_MQTT_PREFIX,
    SENSOR_LIST_CURRENT,
)

with open("./config/config.json", "r") as f:
    config = json.load(f)

amberSiteId = config["amber"]["site_id"]

broker = config["mqtt"]["broker"]
port = config["mqtt"]["port"]
client_id = config["mqtt"]["client_id"]

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def discoveryha(client):
    topic = HOME_ASSISTANT_DISCOVERY_TOPIC
    #for sensor in SENSOR_LIST:
    discoveryMsg = mm.ha_discovery_message() #sensor)
    result = client.publish(topic, json.dumps(discoveryMsg), qos=0, retain=True)
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {topic}")

def publishhastate_current(client, amberdata):
    messagecontent = mm.ha_state_message(amberdata)
    #print(json.dumps(messagecontent["state"]))
    result = client.publish(AMBER_STATE_TOPIC_CURRENT, json.dumps(messagecontent["state"]), qos=0, retain=True)
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {AMBER_STATE_TOPIC_CURRENT}")
    #discoveryMsg = mm.ha_discovery_message()
    #print(json.dumps(messagecontent["attributes"]))
    for sensor in SENSOR_LIST_CURRENT:
        topic = f"{AMBER_MQTT_PREFIX}/{sensor.lower().replace(" ", "_")}/attributes"
        result = client.publish(topic, json.dumps(messagecontent["attributes"]), qos=0, retain=True)
        status = result[0]
        if status != 0:
            print(f"Failed to send message to topic {topic}")

def publishhastate_periods(client, amberdata):
    messagecontent = mm.ha_state_5minPeriods(amberdata)
    #print(json.dumps(messagecontent["state"]))
    result = client.publish(AMBER_STATE_TOPIC_PERIODS, json.dumps(messagecontent["state"]), qos=0, retain=True)
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {AMBER_STATE_TOPIC_PERIODS}")
    for attributemsg in messagecontent["attributes"]:
        topic = f"{AMBER_MQTT_PREFIX}/{attributemsg}/attributes"
        #test = json.dumps(messagecontent["attributes"][attributemsg])
        result = client.publish(topic, json.dumps(messagecontent["attributes"][attributemsg]), qos=0, retain=True)
        status = result[0]
        if status != 0:
            print(f"Failed to send message to topic {topic}")


#if __name__ == '__main__':
#    run()
