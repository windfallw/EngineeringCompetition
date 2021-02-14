from pyb import UART
import utime

try:
    import asyncio
except:
    import uasyncio as asyncio


class US100UART:
    distance = None
    buf_dis = bytearray(2)

    temperature = None
    buf_temper = bytearray(1)

    def __init__(self, port):
        self.uart = UART(port, 9600)
        self.uart.init(9600, bits=8, parity=None, stop=1, timeout=3000)
        utime.sleep_ms(100)

    def isDistance(self):
        if self.uart.any() and self.uart.any() % 2 == 0:
            self.buf_dis = self.uart.read(2)
            self.distance = (self.buf_dis[0] * 256) + self.buf_dis[1]
            return True
        else:
            return False

    async def read_distance(self):
        """
        支持热插拔

        :return: None
        """
        self.uart.write(b'\x55')
        while True:
            await asyncio.sleep_ms(100)
            if self.isDistance():
                break
            else:
                await asyncio.sleep_ms(200)
                if self.isDistance():
                    break
                else:
                    self.distance = None
                    self.uart.read(self.uart.any())
                    self.uart.write(b'\x55')

    async def read_temperature(self):
        """写着玩的"""
        self.uart.write(b'\x50')
        while True:
            await asyncio.sleep_ms(100)
            if self.uart.any():
                self.buf_temper = self.uart.read(1)
                self.temperature = self.buf_temper[0] - 45
                break
            else:
                self.temperature = None
                self.uart.write(b'\x50')
