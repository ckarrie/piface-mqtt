import pifacedigitalio
import socket
import paho.mqtt.client as mqtt
import thread
import time

hostname = socket.gethostname()

mqtt_topic = 'winden/{}/'.format(hostname)
mqtt_input_topic = '{}in/'.format(mqtt_topic)
mqtt_output_topic = '{}out/'.format(mqtt_topic)
mqtt_output_state_topic = '{}state/out/'.format(mqtt_topic)

client = mqtt.Client()
pifacedigital = pifacedigitalio.PiFaceDigital()

in_states = [0, 0, 0, 0, 0, 0, 0, 0]
out_states = [0, 0, 0, 0, 0, 0, 0, 0]

output_topics = {}
for i in range(8):
    output_topics[mqtt_output_topic + str(i)] = i

output_state_topics = {}
for i in range(8):
    output_state_topics[mqtt_output_state_topic + str(i)] = i

def on_connect(client, userdata, flags, rc):
    client.subscribe(mqtt_output_topic + '+')
    print("MQTT Connected, waiting for Topics at", mqtt_topic)

def on_message(client, userdata, msg):
    print("Received: topic='{}' payload='{}'".format(msg.topic, str(msg.payload)))
    if msg.topic in output_topics.keys():
        pin = output_topics[msg.topic]
        if str(msg.payload) in ['ON', '1']:
            pifacedigital.output_pins[pin].turn_on()
            out_states[pin] = 1
            client.publish(mqtt_output_state_topic + str(pin), "ON")
        elif str(msg.payload) in ['OFF', '0']:
            pifacedigital.output_pins[pin].turn_off()
            out_states[pin] = 0
            client.publish(mqtt_output_state_topic + str(pin), "OFF")

    #if msg.topic in output_state_topics.keys():
    #    pin = output_topics[msg.topic]
    #    pin_state = out_states[pin]
    #    state_text = "OFF"
    #    if pin_state == 1:
    #        state_text = "ON"
    #    client.publish(mqtt_input_topic + '{}'.format(event.pin_num), state_text)

def switch_pressed(event):
    #event.chip.output_pins[event.pin_num].turn_on()
    client.publish(mqtt_input_topic + '{}'.format(event.pin_num), "ON")


def switch_unpressed(event):
    #event.chip.output_pins[event.pin_num].turn_off()
    client.publish(mqtt_input_topic + '{}'.format(event.pin_num), "OFF")


def publish_out_state(client):
    while True:
        for topic, pin in output_state_topics.items():
            pin_state = out_states[pin]
            state_text = "OFF"
            if pin_state == 1:
                state_text = "ON"
            client.publish(topic, state_text)
        time.sleep(10)


if __name__ == "__main__":
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("192.168.178.56", 1883, 60)
    client.loop_start()
    thread.start_new_thread(publish_out_state, (client, ))

    listener = pifacedigitalio.InputEventListener(chip=pifacedigital)
    for i in range(4):
        listener.register(i, pifacedigitalio.IODIR_ON, switch_pressed)
        listener.register(i, pifacedigitalio.IODIR_OFF, switch_unpressed)
    listener.activate()

