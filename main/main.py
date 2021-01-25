from pyb import UART
import _thread
import utime
import math

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio

from py.us100 import US100UART
from py.scales import Scales
from py.ws2812 import WS2812

# UART1 connect with Raspberry Pi
pi = UART(1, 115200)  # TX PA9 RX PA10
pi.init(115200, bits=8, parity=0, stop=1, timeout=1000)

# 没加延迟开机以后读的数据会乱
utime.sleep_ms(500)

# Ultrasonic Ranging Module 单位(* mm)
us1 = US100UART(2)  # TX PA2 RX PA3
us2 = US100UART(3)  # TX PD8 RX PD9
us3 = US100UART(4)  # TX C10 RX C11
us4 = US100UART(5)  # TX C12 RX D2

# Electronic scale GND DT SCK VCC 单位(* g)
scale = Scales(d_out='PA4', pd_sck='PA5', offset=0, rate=2.23)
scale.tare()  # 开机校正

# 24 LED ring
ring = WS2812(spi_bus=1, led_count=24, intensity=0.1)


async def rerun(task, wait=50, *args, **kwargs):
    """
    捕捉协程任务异常

    :param task: 协程任务
    :param wait: 单次任务完成后等待时长
    :param args: 函数变量
    :param kwargs: 函数键值对变量
    :return: None
    """
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


def readScale():
    while True:
        try:
            scale.stable_value(reads=5)
        except Exception as err:
            print(err)
        finally:
            utime.sleep_ms(50)


def main_thread():
    loop = asyncio.get_event_loop()
    loop.create_task(rerun(us1.read_distance, wait=0))
    loop.create_task(rerun(us2.read_distance, wait=0))
    loop.create_task(rerun(us3.read_distance, wait=0))
    loop.create_task(rerun(us4.read_distance, wait=0))
    loop.create_task(rerun(readPi))
    loop.create_task(rerun(writePi))
    loop.run_forever()


_thread.start_new_thread(main_thread, ())
_thread.start_new_thread(readScale, ())
