from pyb import UART
import _thread
import utime

try:
    import asyncio
except:
    import uasyncio as asyncio

from py.us100 import US100UART
from py.scales import Scales

# UART1 connect with Raspberry Pi
pi = UART(1, 115200)  # TX PA9 RX PA10
pi.init(115200, bits=8, parity=0, stop=1, timeout=1000)

# Ultrasonic Ranging Module 单位(* mm)
us1 = US100UART(2)  # TX PA2 RX PA3
us2 = US100UART(3)  # TX PD8 RX PD9
us3 = US100UART(4)  # TX C10 RX C11
us4 = US100UART(5)  # TX C12 RX D2

# Electronic scale GND DT SCK VCC 单位(* g)
scale = Scales(d_out='PA4', pd_sck='PA5', offset=0, rate=2.23)
scale.tare()  # 开机校正


async def rerun(task, wait=50, *args, **kwargs):
    while True:
        try:
            await task(*args, **kwargs)
        except Exception as err:
            print(err)
        finally:
            await asyncio.sleep_ms(wait)


async def readPi():
    if pi.any():
        print(pi.read())


async def writePi():
    print(us1.distance, us2.distance, us3.distance, us4.distance, scale.weight)


async def readScales():
    scale.stable_value(reads=3, delay_us=1)


def readScale():
    while True:
        try:
            scale.stable_value(reads=3, delay_us=1)
        except Exception as err:
            print(err)
        finally:
            utime.sleep_ms(50)


def main_thread():
    loop = asyncio.get_event_loop()
    loop.create_task(us1.read_dis())
    loop.create_task(us2.read_dis())
    loop.create_task(us3.read_dis())
    loop.create_task(us4.read_dis())
    loop.create_task(rerun(readScales))
    loop.create_task(rerun(readPi))
    loop.create_task(rerun(writePi))
    loop.run_forever()


_thread.start_new_thread(main_thread, ())
# _thread.start_new_thread(readScale, ())
