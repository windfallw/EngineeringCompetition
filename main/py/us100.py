from pyb import UART

try:
    import asyncio
except:
    import uasyncio as asyncio


class US100UART:
    distance = None
    temper = None
    buf_dis = bytearray(2)
    buf_temper = bytearray(1)

    def __init__(self, uart):
        self.uart = UART(uart, 9600)
        self.uart.init(9600, bits=8, parity=None, stop=1, timeout=3000)

    async def read_dis(self):
        while True:
            try:
                self.uart.write(b'\x55')
                while True:
                    await asyncio.sleep_ms(100)
                    if self.uart.any() >= 2:
                        self.buf_dis = self.uart.read(2)
                        self.distance = (self.buf_dis[0] * 256) + self.buf_dis[1]
                        break
                    elif self.uart.any():
                        self.uart.read(1)
                        self.uart.write(b'\x55')
                    else:
                        self.distance = None
                        self.uart.write(b'\x55')
            except Exception:
                pass

    async def read_temper(self):
        while True:
            self.uart.write(b'\x50')
            while True:
                await asyncio.sleep_ms(100)
                if self.uart.any():
                    self.buf_temper = self.uart.read(1)
                    self.temper = self.buf_temper[0] - 45
                    break
                else:
                    self.temper = None
                    self.uart.write(b'\x55')
