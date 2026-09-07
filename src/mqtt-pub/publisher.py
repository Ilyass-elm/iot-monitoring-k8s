
# -*- coding: utf-8 -*-
# python mqtt client - subscriber
import paho.mqtt.client as mqtt
import random
import time

# broker settings
BROKER_IP = "broker"
BROKER_PORT = 1883
KEEPALIVE = 30
CLIENT_ID = "pseudo-sensor"
TOPIC = 'sensor/temp'
 
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

client = mqtt.Client(client_id=CLIENT_ID, clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
client.on_connect = on_connect

client.connect(BROKER_IP, BROKER_PORT, KEEPALIVE)
 
print("Connected to MQTT Broker: " + BROKER_IP + ":" + str(BROKER_PORT))

while 1:
    number = random.randrange(18, 45)
    client.publish(topic=TOPIC, payload=number)
    print("published: " + str(number))
    time.sleep(2)
    
