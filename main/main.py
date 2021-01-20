from pyb import UART
import _thread
import utime

try:
    import asyncio
except:
    import uasyncio as asyncio

from py.us100 import US100UART
from py.hx711 import HX711

# UART1 connect with Raspberry Pi
pi = UART(1, 115200)  # TX PA9 RX PA10
pi.init(115200, bits=8, parity=0, stop=1, timeout=1000)

# Ultrasonic Ranging Module 单位(* mm)
us1 = US100UART(2)  # TX PA2 RX PA3
us2 = US100UART(3)  # TX PD8 RX PD9
us3 = US100UART(4)  # TX C10 RX C11
us4 = US100UART(5)  # TX C12 RX D2

# GND DT SCK VCC
driver = HX711(d_out='PA4', pd_sck='PA5')


def readUart():
    while True:
        if pi.any():
            print(pi.read())
        utime.sleep_ms(50)


async def print_ALL():
    while True:
        # print(us1.distance, us2.distance, us3.distance, us4.distance)
        print(driver.read())
        await asyncio.sleep_ms(50)


def sensor_thread():
    scheduler = asyncio.get_event_loop()
    scheduler.create_task(us1.read_dis())
    scheduler.create_task(us2.read_dis())
    scheduler.create_task(us3.read_dis())
    scheduler.create_task(us4.read_dis())
    scheduler.create_task(print_ALL())
    scheduler.run_forever()


_thread.start_new_thread(sensor_thread, ())
_thread.start_new_thread(readUart, ())
