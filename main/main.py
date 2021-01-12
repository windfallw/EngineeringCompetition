from py.hcsr04 import hcsr04
from py.us100 import US100
from pyb import UART
import _thread
import utime

# Ultrasonic Ranging Module
# GND DT SCK VCC
urm1 = hcsr04(trigger_pin='PD9', echo_pin='PD10')
urm2 = hcsr04(trigger_pin='PD11', echo_pin='PD12')

pi = UART(1, 115200)
pi.init(115200, bits=8, parity=None, stop=1)


def readUart():
    if pi.any():
        print(pi.read())


def sensor_thread():
    while True:
        try:
            print(urm1.distance())

        except OSError as err:
            print('Error occur when getting sensor:', err)
        utime.sleep_ms(50)


_thread.start_new_thread(sensor_thread, ())
