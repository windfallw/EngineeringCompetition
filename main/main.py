from pyb import UART, Timer, Pin
import collections
import binascii
import _thread
import utime
import json

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio

from py.us100 import US100UART
from py.scales import Scales
from py.ws2812 import WS2812

# UART1 connect with Raspberry Pi
pi = UART(1, 115200)  # TX PA9 RX PA10
pi.init(115200, bits=8, parity=None, stop=1, timeout=0)

# 没加延迟开机以后读的数据会乱
utime.sleep_ms(500)

# Ultrasonic Ranging Module 单位(* mm)
us1 = US100UART(2)  # TX PA2 RX PA3
us2 = US100UART(3)  # TX PD8 RX PD9
us3 = US100UART(4)  # TX C10 RX C11
us4 = US100UART(5)  # TX C12 RX PD2

# Electronic scale GND DT SCK VCC 单位(* g)
scale = Scales(d_out='PC4', pd_sck='PC5', offset=0, rate=2.23)
scale.tare()  # 开机校正

# 24 RGB LED ring DOUT(PB15)
ring = WS2812(spi_bus=2, led_count=24, intensity=0.1)

# Hall sensor detect pin
hall = Pin('PD3', Pin.IN, Pin.PULL_UP)

# time = 1 // freq so (freq = 0.1) == (time = 10s)
tim = Timer(1)
tim.init(freq=0.1, callback=lambda t: ring.light_off())


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
            ...
            # print(err)
        finally:
            await asyncio.sleep_ms(wait)


async def readPi(rx_split=b'#'):
    if pi.any():
        line = pi.readline()
        print(line)
        if line.rfind(rx_split) > 0:
            raw = line.rsplit(rx_split, 1)
            crc32 = int(raw[1].replace(b'\r\n', b''))
            if crc32 == binascii.crc32(raw[0]):
                result = raw[0].decode('utf-8', 'strict')
                # print(result)
            else:
                raise Exception("crc32 checksum error")
        else:
            raise Exception("uart received an error data")


async def writePi(tx_split=b'*'):
    data = collections.OrderedDict()
    data['us1'] = us1.distance
    data['us2'] = us2.distance
    data['us3'] = us3.distance
    data['us4'] = us4.distance
    data['scale'] = scale.weight
    data['hall'] = hall.value()

    if data['hall']:
        data['hall'] = True
    else:
        data['hall'] = False

    result = json.dumps(data).encode('utf-8', 'strict')
    raw = b'%s%s%d\r\n' % (result, tx_split, binascii.crc32(result))
    pi.write(raw)
    # print(raw)


async def shine():
    while hall.value():
        for data in ring.data_generator():
            if not hall.value():
                tim.counter(0)
                ring.light_on()
                break
            ring.set_intensity(ring.common_intensity)
            ring.show(data)
            await asyncio.sleep_ms(0)

    if not ring.light and not hall.value():
        ring.clear()

    await asyncio.sleep_ms(0)


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
    loop.create_task(rerun(writePi, wait=30, tx_split=b'*'))
    loop.create_task(rerun(readPi, wait=50, rx_split=b'#'))
    loop.create_task(rerun(shine, wait=0))
    loop.run_forever()


_thread.start_new_thread(main_thread, ())
_thread.start_new_thread(readScale, ())
