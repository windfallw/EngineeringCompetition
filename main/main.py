from py.us100 import US100UART
from pyb import UART
import _thread
import utime

try:
    import asyncio
except:
    import uasyncio as asyncio

# GND DT SCK VCC

# UART1 connect with Raspberry Pi
pi = UART(1, 115200)  # TX PA9 RX PA10
pi.init(115200, bits=8, parity=0, stop=1)

# Ultrasonic Ranging Module
us1 = US100UART(2)  # TX PA2 RX PA3
us2 = US100UART(3)  # TX PD8 RX PD9
us3 = US100UART(4)  # TX C10 RX C11
us4 = US100UART(5)  # TX C12 RX D2


def readUart():
    if pi.any():
        print(pi.read())


def sensor_thread():
    asyncio.run(us1.read_all())


_thread.start_new_thread(sensor_thread, ())
