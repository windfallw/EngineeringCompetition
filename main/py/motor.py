from machine import Pin
import utime


class NEMA17:
    STEPS_PER_REV = 800

    def __init__(self, en, step, direction):
        self.en_pin = Pin(en, Pin.OUT, value=1)  # disable driver
        self.step_pin = Pin(step, Pin.OUT)
        self.dir_pin = Pin(direction, Pin.OUT, value=0)  # low voltage clockwise || high voltage Counterclockwise

    def on(self):
        self.en_pin.value(0)

    def off(self):
        self.en_pin.value(1)

    def step(self):
        self.on()

        self.dir_pin.value(0)

        for _ in range(self.STEPS_PER_REV):
            self.step_pin.value(1)
            utime.sleep_us(500)
            self.step_pin.value(0)
            utime.sleep_us(500)

        utime.sleep_us(500)
        self.off()

    def run(self):
        self.dir_pin.value(1)

        for _ in range(self.STEPS_PER_REV):
            self.step_pin.value(1)
            utime.sleep_us(2000)
            self.step_pin.value(0)
            utime.sleep_us(2000)

        utime.sleep(1)
        self.dir_pin.value(0)

        for _ in range(self.STEPS_PER_REV * 2):
            self.step_pin.value(1)
            utime.sleep_us(1000)
            self.step_pin.value(0)
            utime.sleep_us(1000)

        utime.sleep(1)
