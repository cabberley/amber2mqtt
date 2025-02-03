"""MQTT functions for Subscribing and publishing to MQTT"""

import json
import os
from paho.mqtt import client as mqtt_client
import mqttmessages as mm
from const import (
    AMBER_DISCOVERY_TOPIC,
    AMBER_FORECAST_DISCOVERY_TOPIC,
    AEMO_DISCOVERY_TOPIC,
    AMBER_STATE_TOPIC_CURRENT,
    AMBER_STATE_TOPIC_PERIODS,
    AMBER_MQTT_PREFIX,
    SENSOR_LIST_CURRENT,
    AEMO_STATE_TOPIC_CURRENT,
)

if os.path.isfile("/data/options.json"):
    with open("/data/options.json", "r") as f:
        config = json.load(f)
else: 
    with open("./data/options.json", "r") as f:
        config = json.load(f)

# amberSiteId = config["amber"]["site_id"]
username = None
password = None
broker = config["mqtt"]["broker"]
port = config["mqtt"]["port"]
client_id = config["mqtt"]["client_id"]
for key in config["mqtt"]:
    if key == "username":
        username = config["mqtt"]["username"]
    if key == "password":
        password = config["mqtt"]["password"]

def mqttConnectBroker():
    """Connect to the MQTT Broker"""
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_subscribe(client, userdata, mid, reason_code_list, properties):
        # Since we subscribed only for a single channel, reason_code_list contains
        # a single entry
        if reason_code_list[0].is_failure:
            print(f"Broker rejected you subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_message(client, userdata, message):
        # userdata is the structure we choose to provide, here it's a list()
        userdata = message.payload
        print(userdata)
        if userdata == b"online":
            PublishDiscoveryAmberEntities(client)
            PublishDiscoveryAemoEntities(client)
        # We only want to process 10 messages
        # if len(userdata) >= 10:
        #    client.unsubscribe("$SYS/#")

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
    if username not in (None, ""):
        client.username_pw_set(username, password)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.connect(broker, port)
    return client


def PublishDiscoveryAmberEntities(client):
    """Publish the Amber Entities to Home Assistant"""
    #topic = HOME_ASSISTANT_DISCOVERY_TOPIC
    # for sensor in SENSOR_LIST:
    discoveryMsg = mm.amberDiscoveryMessage()  # sensor)
    result = client.publish(AMBER_DISCOVERY_TOPIC, json.dumps(discoveryMsg), qos=0, retain=True)
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {AMBER_DISCOVERY_TOPIC}")


def PublishDiscoveryAemoEntities(client):
    """Publish the AEMO Entities to Home Assistant"""
    #topic = HOME_ASSISTANT_DISCOVERY_TOPIC
    # for sensor in SENSOR_LIST:
    discoveryMsg = mm.aemoDiscoveryMessage()  # sensor)
    result = client.publish(AEMO_DISCOVERY_TOPIC, json.dumps(discoveryMsg), qos=0, retain=True)
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {AEMO_DISCOVERY_TOPIC}")


def publishAmberStateCurrent(client, amberdata):
    """Publish the current Amber state to MQTT"""
    messageContent = mm.amberStateMessage(amberdata)
    # print(json.dumps(messageContent["state"]))
    result = client.publish(
        AMBER_STATE_TOPIC_CURRENT,
        json.dumps(messageContent["state"]),
        qos=0,
        retain=True,
    )
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {AMBER_STATE_TOPIC_CURRENT}")
    # discoveryMsg = mm.amberDiscoveryMessage()
    # print(json.dumps(messageContent["attributes"]))
    for sensor in SENSOR_LIST_CURRENT:
        topic = f"{AMBER_MQTT_PREFIX}/{sensor.lower().replace(' ', '_')}/attributes"
        result = client.publish(
            topic, json.dumps(messageContent["attributes"]), qos=0, retain=True
        )
        status = result[0]
        if status != 0:
            print(f"Failed to send message to topic {topic}")


def publishAmberStatePeriods(client, amberdata):
    """Publish the Amber state to MQTT for the 12 periods"""
    messageContent = mm.amberState5MinPeriods(amberdata)
    # print(json.dumps(messageContent["state"]))
    result = client.publish(
        AMBER_STATE_TOPIC_PERIODS,
        json.dumps(messageContent["state"]),
        qos=0,
        retain=True,
    )
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {AMBER_STATE_TOPIC_PERIODS}")
    for attributemsg in messageContent["attributes"]:
        topic = f"{AMBER_MQTT_PREFIX}/{attributemsg}/attributes"
        # test = json.dumps(messageContent["attributes"][attributemsg])
        result = client.publish(
            topic,
            json.dumps(messageContent["attributes"][attributemsg]),
            qos=0,
            retain=True,
        )
        status = result[0]
        if status != 0:
            print(f"Failed to send message to topic {topic}")


def publishAemoStateCurrent(client, aemoData):
    """Publish the AEMO state to MQTT"""
    messageContent = mm.aemoCurrentStateMessage(aemoData)
    result = client.publish(
        AEMO_STATE_TOPIC_CURRENT,
        json.dumps(messageContent["state"]),
        qos=0,
        retain=True,
    )
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {AMBER_STATE_TOPIC_CURRENT}")
    for attributeMsg in messageContent["attributes"]:
        topic = f"{AMBER_MQTT_PREFIX}/{attributeMsg}/attributes"
        result = client.publish(
            topic,
            json.dumps(messageContent["attributes"][attributeMsg]),
            qos=0,
            retain=True,
        )
        status = result[0]
        if status != 0:
            print(f"Failed to send message to topic {topic}")


# if __name__ == '__main__':
#    run()
