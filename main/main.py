from py.hcsr04 import HCSR04
from py.us100 import US100
from pyb import UART
import _thread
import utime

'''Ultrasonic Ranging Module'''

urm1 = HCSR04(trigger_pin='PD9', echo_pin='PD10')
urm2 = HCSR04(trigger_pin='PD11', echo_pin='PD12')
# urm3 = HCSR04(trigger_pin='PD11', echo_pin='PD12')
# urm4 = HCSR04(trigger_pin='PD11', echo_pin='PD12')

pi = UART(1, 115200)
pi.init(115200, bits=8, parity=None, stop=1)


def readUart():
    if pi.any():
        print(pi.read())


def sensor_thread():
    while True:
        try:
            print(urm1.distance_cm())

        except OSError as err:
            print('Error occur when getting sensor:', err)
        utime.sleep_ms(50)


_thread.start_new_thread(sensor_thread, ())
