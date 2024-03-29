"""
sudo raspi-config:
- setup Hostname
- enable SPI

sudo apt install python-pip
sudo apt install screen
sudo pip install pifacecommon
sudo pip install pifacedigitalio
sudo pip install paho-mqtt

Enable via cron:
crontab -e
@reboot  sleep 60 && /usr/bin/screen -dmS py_mqtt python /home/pi/mqtt.py

"""
import pifacedigitalio
import socket
import paho.mqtt.client as mqtt
import thread
import time
import datetime
import json
import uuid
import re

MQTT_BROKER_HOST = '192.168.178.71'

hostname = socket.gethostname()
mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

mqtt_topic = 'winden/{}/piface/'.format(hostname)
mqtt_input_topic = '{}in/'.format(mqtt_topic)
mqtt_output_topic = '{}out/'.format(mqtt_topic)
mqtt_device_topic = '{}infos/'.format(mqtt_topic)
#mqtt_output_state_topic = '{}state/out/'.format(mqtt_topic)
#mqtt_input_state_topic = '{}state/in/'.format(mqtt_topic)

client = mqtt.Client()
pifacedigital = pifacedigitalio.PiFaceDigital()

in_states = [0, 0, 0, 0, 0, 0, 0, 0]
out_states = [0, 0, 0, 0, 0, 0, 0, 0]

output_topics = {}
for i in range(8):
    output_topics[mqtt_output_topic + str(i)] = i

input_topics = {}
for i in range(8):
    input_topics[mqtt_input_topic + str(i)] = i

#output_state_topics = {}
#for i in range(8):
#    output_state_topics[mqtt_output_state_topic + str(i)] = i

#input_state_topics = {}
#for i in range(8):
#    input_state_topics[mqtt_input_state_topic + str(i)] = i

def publish_homeassistant(client):
    homeassistant_switch_topic = "homeassistant/switch/{}/sw{}/config"
    for switch_port in range(8):
        topic = homeassistant_switch_topic.format(hostname, switch_port)
        payload = {
            "name": "{} Switch {}".format(hostname, switch_port), 
            "unique_id": "{}-sw{}".format(hostname, switch_port), 
            "device": {
                "identifiers": hostname + "-wlan", 
                "connections": [
                    ["mac", mac_address]
                ], 
                "manufacturer": "Raspberry Pi Foundation", 
                "model": "Raspberry Pi 1", 
                "name": hostname, 
                "sw_version": "1"
            }, 
            "state_topic": mqtt_output_topic + str(switch_port), #"winden/pipool/piface/out/5", 
            "command_topic": mqtt_output_topic + str(switch_port), 
            "state_on": "true", 
            "state_off": "false", 
            "payload_on": "true", 
            "payload_off": "false",
            "icon": "mdi:lightbulb-on"
        }
        client.publish(topic, json.dumps(payload))
        print("[publish_homeassistant] published", topic)
    # Device classes: https://developers.home-assistant.io/docs/en/entity_binary_sensor.html#available-device-classes
    homeassistant_binary_sensor_topic = "homeassistant/binary_sensor/{}/bs{}/config"
    for input_nr in range(8):
        topic = homeassistant_binary_sensor_topic.format(hostname, input_nr)
        payload = {
            "name": "{} Input {}".format(hostname, input_nr), 
            "unique_id": "{}-bs{}".format(hostname, input_nr), 
            "device": {
                "identifiers": hostname + "-wlan", 
                "connections": [
                    ["mac", mac_address]
                ], 
                "manufacturer": "Raspberry Pi Foundation", 
                "model": "Raspberry Pi 1", 
                "name": hostname, 
                "sw_version": "1"
            }, 
            "state_topic": mqtt_input_topic + str(input_nr), #"winden/pipool/piface/in/5", 
            "payload_on": "true", 
            "payload_off": "false",
            "device_class": "power",
            #"icon": "mdi:electric-switch"
        }
        client.publish(topic, json.dumps(payload))
        print("[publish_homeassistant] published", topic)
        

def on_connect(client, userdata, flags, rc):
    client.subscribe(mqtt_output_topic + '+')
    print("MQTT Connected, waiting for Topics at '{}'".format(mqtt_output_topic))
    #publish_homeassistant(client)

def on_message(client, userdata, msg):
    print("Received: topic='{}' payload='{}'".format(msg.topic, str(msg.payload)))
    if msg.topic in output_topics.keys():
        pin = output_topics[msg.topic]
        if str(msg.payload) in ['ON', '1', 'true']:
            pifacedigital.output_pins[pin].turn_on()
            out_states[pin] = 1
            #client.publish(mqtt_output_state_topic + str(pin), "true")
        elif str(msg.payload) in ['OFF', '0', 'false']:
            pifacedigital.output_pins[pin].turn_off()
            out_states[pin] = 0
            #client.publish(mqtt_output_state_topic + str(pin), "OFF")

    #if msg.topic in output_state_topics.keys():
    #    pin = output_topics[msg.topic]
    #    pin_state = out_states[pin]
    #    state_text = "false"
    #    if pin_state == 1:
    #        state_text = "true"
    #    client.publish(mqtt_input_topic + '{}'.format(event.pin_num), state_text)
    
def switch_pressed(event):
    #event.chip.output_pins[event.pin_num].turn_on()
    in_states[event.pin_num] = 1
    client.publish(mqtt_input_topic + '{}'.format(event.pin_num), "true")


def switch_unpressed(event):
    #event.chip.output_pins[event.pin_num].turn_off()
    in_states[event.pin_num] = 0
    client.publish(mqtt_input_topic + '{}'.format(event.pin_num), "false")


def publish_inout_state(client, piface_chip):
    while True:
        for topic, pin in output_topics.items():
            pin_state = out_states[pin]
            state_text = "false"
            if pin_state == 1:
                state_text = "true"
            client.publish(topic, state_text)
            print("[Loop] Publish topic='{}' payload='{}'".format(topic, state_text))
        for topic, pin in input_topics.items():
            pin_state = piface_chip.input_pins[pin].value
            if in_states[pin] != pin_state:
                in_states[pin] = pin_state
            state_text = "false"
            if pin_state == 1:
                state_text = "true"
            client.publish(topic, state_text)
            print("[Loop] Publish topic='{}' payload='{}'".format(topic, state_text))
        client.publish(mqtt_device_topic + 'datetime', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        time.sleep(20)
        
def publish_homeassistant_discovery(client):
    while True:
        publish_homeassistant(client)
        print("[Loop] Publish publish_homeassistant for discovery")
        time.sleep(600)
        
if __name__ == "__main__":
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER_HOST, 1883, 60)
    client.loop_start()
    thread.start_new_thread(publish_inout_state, (client, pifacedigital))
    thread.start_new_thread(publish_homeassistant_discovery, (client,))

    listener = pifacedigitalio.InputEventListener(chip=pifacedigital)
    for i in range(4):
        listener.register(i, pifacedigitalio.IODIR_ON, switch_pressed)
        listener.register(i, pifacedigitalio.IODIR_OFF, switch_unpressed)
    listener.activate()




