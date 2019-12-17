import pifacedigitalio
import socket
import paho.mqtt.client as mqtt
import thread
import time

hostname = socket.gethostname()

mqtt_topic = 'winden/{}/piface/'.format(hostname)
mqtt_input_topic = '{}in/'.format(mqtt_topic)
mqtt_output_topic = '{}out/'.format(mqtt_topic)
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

def on_connect(client, userdata, flags, rc):
    client.subscribe(mqtt_output_topic + '+')
    print("MQTT Connected, waiting for Topics at", mqtt_output_topic)

def on_message(client, userdata, msg):
    print("Received: topic='{}' payload='{}'".format(msg.topic, str(msg.payload)))
    if msg.topic in output_topics.keys():
        pin = output_topics[msg.topic]
        if str(msg.payload) in ['ON', '1']:
            pifacedigital.output_pins[pin].turn_on()
            out_states[pin] = 1
            #client.publish(mqtt_output_state_topic + str(pin), "ON")
        elif str(msg.payload) in ['OFF', '0']:
            pifacedigital.output_pins[pin].turn_off()
            out_states[pin] = 0
            #client.publish(mqtt_output_state_topic + str(pin), "OFF")

    #if msg.topic in output_state_topics.keys():
    #    pin = output_topics[msg.topic]
    #    pin_state = out_states[pin]
    #    state_text = "OFF"
    #    if pin_state == 1:
    #        state_text = "ON"
    #    client.publish(mqtt_input_topic + '{}'.format(event.pin_num), state_text)
    
def switch_pressed(event):
    #event.chip.output_pins[event.pin_num].turn_on()
    in_states[event.pin_num] = 1
    client.publish(mqtt_input_topic + '{}'.format(event.pin_num), "ON")


def switch_unpressed(event):
    #event.chip.output_pins[event.pin_num].turn_off()
    in_states[event.pin_num] = 0
    client.publish(mqtt_input_topic + '{}'.format(event.pin_num), "OFF")


def publish_inout_state(client, piface_chip):
    while True:
        for topic, pin in output_topics.items():
            pin_state = out_states[pin]
            state_text = "OFF"
            if pin_state == 1:
                state_text = "ON"
            client.publish(topic, state_text)
            print("Publish", topic, state_text)
        for topic, pin in input_topics.items():
            pin_state = piface_chip.input_pins[pin].value
            if in_states[pin] != pin_state:
                in_states[pin] = pin_state
            state_text = "OFF"
            if pin_state == 1:
                state_text = "ON"
            client.publish(topic, state_text)
            print("Publish", topic, state_text)
        time.sleep(30)
        
if __name__ == "__main__":
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("192.168.178.56", 1883, 60)
    client.loop_start()
    thread.start_new_thread(publish_inout_state, (client, pifacedigital))

    listener = pifacedigitalio.InputEventListener(chip=pifacedigital)
    for i in range(4):
        listener.register(i, pifacedigitalio.IODIR_ON, switch_pressed)
        listener.register(i, pifacedigitalio.IODIR_OFF, switch_unpressed)
    listener.activate()




