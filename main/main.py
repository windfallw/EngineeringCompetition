from pyb import Timer, Pin, hard_reset
import _thread

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio

from py.berry import RaspberryPi
from py.motor import NEMA17
from py.us100 import US100UART
from py.scales import Scales
from py.ws2812 import WS2812


def funcHandler(func):
    """修饰响应树莓派命令的函数"""

    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
            pi.result['code'] = 200

        except Exception as err:
            pi.result['code'] = 401
            pi.result['msg'] = str(err)

        finally:
            pi.write_task_result()

    return inner_function


@funcHandler
def set_offset(kwargs):
    if scale is None:
        raise Exception("电子秤异常")

    if 'offset' in kwargs:
        scale.offset = kwargs['offset']
        pi.result['msg'] = 'set offset %s' % scale.offset

    else:
        scale.offset = scale.raw
        pi.result['msg'] = 'auto set offset %s' % scale.raw

    pi.result['data'] = {'offset': scale.offset}


@funcHandler
def ws2812(kwargs):
    if 'force_open' in kwargs:
        if {'rgb_intensity', 'light_intensity', 'light_rgb'} <= set(kwargs):
            ring.rgb_intensity = kwargs['rgb_intensity']
            ring.light_intensity = kwargs['light_intensity']
            ring.light_rgb = kwargs['light_rgb']
            pi.result['msg'] = 'config save done'
            if ring.light:
                ring.light = False
        if kwargs['force_open']:
            ring.force_open = True

    pi.result['data'] = {
        'rgb_intensity': ring.rgb_intensity,
        'light_intensity': ring.light_intensity,
        'light_rgb': ring.light_rgb
    }


@funcHandler
def reboot(kwargs):
    pi.result['code'] = 200
    pi.result['msg'] = 'rebooting'
    # 在重启前将响应信息发送。
    pi.write_task_result()
    hard_reset()


# eval or exec允许访问的函数
allow_func = {'set_offset': set_offset, 'ws2812': ws2812, 'reboot': reboot}


async def readData():
    """读取树莓派发送的指令并执行"""

    task = pi.readline()
    if task is not None:
        if task[0] in allow_func:
            allow_func[task[0]](task[1])
        else:
            pi.result['code'] = 401
            pi.result['msg'] = "不支持的方法!"
            pi.write_task_result()


async def writeData():
    """读取当前所有传感器信息并发送给树莓派"""

    pi.us100['us1'] = us1.distance
    pi.us100['us2'] = us2.distance
    pi.us100['us3'] = us3.distance
    pi.us100['us4'] = us4.distance

    if scale:
        pi.data['scale'] = {'weight': scale.weight, 'offset': scale.offset}
    else:
        pi.data['scale'] = None

    if hall.value():
        pi.data['hall'] = True
    else:
        pi.data['hall'] = False

    pi.writeline(pi.data)


async def shine():
    """刷新打光灯状态"""

    while hall.value():
        for data in ring.data_generator():
            if not hall.value():
                tim.counter(0)
                ring.light_on()
                break
            ring.set_intensity(ring.rgb_intensity)
            ring.show(data)
            await asyncio.sleep_ms(0)

    if ring.force_open:
        ring.force_open = False
        tim.counter(0)
        if not ring.light:
            ring.light_on()

    elif not ring.light and not hall.value():
        ring.clear()

    await asyncio.sleep_ms(0)


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


def async_thread():
    """协程+多线程"""

    loop = asyncio.get_event_loop()
    loop.create_task(rerun(us1.read_distance, wait=0))
    loop.create_task(rerun(us2.read_distance, wait=0))
    loop.create_task(rerun(us3.read_distance, wait=0))
    loop.create_task(rerun(us4.read_distance, wait=0))

    loop.create_task(rerun(readData, wait=50))
    loop.create_task(rerun(writeData, wait=50))

    loop.create_task(rerun(shine, wait=50))
    loop.run_forever()


def main_thread():
    """支持热插拔，用于读电子秤，单独一个线程是因为电子秤取得稳定的值需要较多延迟函数，而改成协程又过于冗余繁琐。减少每次权重取值的reads数可以加快。"""

    global scale
    while True:
        try:
            if scale is None:
                scale = Scales(d_out='PC4', pd_sck='PC5', offset=0, rate=2.23)
            else:
                scale.stable_value(reads=5)
        except Exception as error:
            if str(error) == 'DeviceIsNotReady':
                scale = None
            else:
                print(error)


if __name__ == '__main__':
    # UART1 connect with Raspberry Pi TX PA9 RX PA10
    pi = RaspberryPi(port=1)

    # Ultrasonic Ranging Module 单位(* mm)
    us1 = US100UART(port=2)  # TX PA2 RX PA3
    us2 = US100UART(port=3)  # TX PD8 RX PD9
    us3 = US100UART(port=4)  # TX C10 RX C11
    us4 = US100UART(port=5)  # TX C12 RX PD2

    # Electronic scale GND DT SCK VCC 单位(* g) 电子称模块暂时废弃
    scale = None
    # try:
    #     scale = Scales(d_out='PC4', pd_sck='PC5', offset=0, rate=2.23)
    # except Exception as err:
    #     scale = None
    #     print(err)

    # 24 RGB LED ring DOUT(PB15)
    ring = WS2812(spi_bus=2, led_count=24, intensity=0.1)

    # Hall sensor detect pin
    hall = Pin('PD3', Pin.IN, Pin.PULL_UP)

    # time = 1 // freq so (freq = 0.1) == (time = 10s)
    tim = Timer(1, freq=0.1)
    tim.callback(ring.light_off)

    _thread.start_new_thread(async_thread, ())
    # _thread.start_new_thread(main_thread, ())

    # m1 = NEMA17(en=5, step=16, direction=17)
    # m2 = NEMA17(en=25, step=26, direction=27)

# 主程序不要运行死循环，否则串口终端会阻塞，且进入raw REPL mode上传代码也容易卡顿。
