import time
import machine
from machine import Pin, PWM
import ubinascii
from umqtt.simple import MQTTClient

p5 = Pin(5, Pin.OUT)
pwm = PWM(p5)

# Set the pulse every 20ms
pwm.freq(50)

# Set initial duty to 0
# to turn off the pulse
pwm.duty(0)

# Default MQTT server to connect to
SERVER = "test.mosquitto.org"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = b"/vend/"


# Creates a function for mapping the 0 to 180 degrees
# to 20 to 120 pwm duty values
def servo_map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


# Creates another function for turning
# the servo according to input angle
# mg995 duty vals - max(125) min(11) - we set the values to 10 and 90 to get 0 - 180 deg
def servo(pin, angle):
    pin.duty(servo_map(angle, 0, 180, 10, 90))


# dispense method, rotates the servo to 180 degrees and returns to 0
def dispense():
    servo(pwm, 180)
    time.sleep(1)
    servo(pwm, 0)
    time.sleep(4)


def sub_cb(topic, msg):
    print("incoming message => ", (topic, msg))
    dispense()
    # if msg == b"dispense":
    #     dispense()


def connect_and_subscribe():
    client = MQTTClient(CLIENT_ID, SERVER)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(TOPIC + "dispense")
    print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC + "dispense"))
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
            # micropython.mem_info()
            client.wait_msg()
            new_message = client.check_msg()

            if new_message != 'None':
                client.publish(TOPIC + "status", "dispense happened!")
                time.sleep(1)
    except OSError as e:
        restart_and_reconnect()
