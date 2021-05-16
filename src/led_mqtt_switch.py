import time
import machine
from machine import Pin
import ubinascii
from umqtt.simple import MQTTClient


# ESP8266 ESP-12 modules have blue, active-low LED on GPIO2, replace
# with something else if needed.
led = Pin(5, Pin.OUT, value=1)

# Default MQTT server to connect to
SERVER = "test.mosquitto.org"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = b"/mydevice/"

def sub_cb(topic, msg):
    print("incoming message => ", (topic, msg))
    on = led.on
    off = led.off
    if msg == b"1":
        on()
    elif msg == b"0":
        off()

def connect_and_subscribe():
    client = MQTTClient(CLIENT_ID, SERVER)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(TOPIC+"set")
    print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC+"set"))
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(5)
    machine.reset()

def main():
    try:
        client = connect_and_subscribe()
    except OSError as e:
        restart_and_reconnect()
    
    try:
        while 1:
            #micropython.mem_info()
            client.wait_msg()
            new_message = client.check_msg()

            if new_message != 'None':
                client.publish(TOPIC+"status", str(led.value()))
                time.sleep(1)
    except OSError as e:
        restart_and_reconnect()

