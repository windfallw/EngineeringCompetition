from pyb import UART
import utime

try:
    import asyncio
except:
    import uasyncio as asyncio


class US100UART:
    distance = None
    temper = None
    buf = bytearray(2)
    t = 0

    def __init__(self, uart):
        self.uart = UART(uart, 9600)
        self.uart.init(9600, bits=8, parity=None, stop=1)

    async def read_dis(self):
        self.uart.write(b'\x55')
        self.buf[0] = 0
        self.buf[1] = 0

        self.t = utime.ticks_ms()

        while not self.uart.any():
            if utime.ticks_diff(utime.ticks_ms(), self.t) > 100:
                await asyncio.sleep(1)

        self.uart.readinto(self.buf, 2)
        self.distance = (self.buf[0] * 256) + self.buf[1]

        return self.distance

    async def read_temper(self):
        self.uart.write(b'\x50')
        self.buf[0] = 0

        self.t = utime.ticks_ms()

        while not self.uart.any():
            if utime.ticks_diff(utime.ticks_ms(), self.t) > 100:
                await asyncio.sleep(1)

        self.uart.readinto(self.buf, 1)
        self.temper = self.buf[0] - 45

        return self.temper

    async def read_all(self):
        while True:
            try:
                await asyncio.gather(self.read_dis(), self.read_temper())
                print(self.distance, self.temper)
            except Exception as err:
                print('Error:', err)
