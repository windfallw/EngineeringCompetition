from pyb import Pin
import utime


class NEMA17:
    STEPS_PER_REV = 200

    def __init__(self, en, step, direction):
        self.en_pin = Pin(en, Pin.OUT, value=1)  # disable driver at initial
        self.step_pin = Pin(step, Pin.OUT)
        self.dir_pin = Pin(direction, Pin.OUT, value=0)  # low voltage clockwise || high voltage Counterclockwise

    def on(self):
        self.en_pin.value(0)

    def off(self):
        self.en_pin.value(1)

    def step(self, clockwise=True, delay=200):
        """
        Each pulse sent here steps the motor by whatever number of steps or microsteps that has been set by MS1, MS2 and MS3 settings.

        :return: None
        """

        self.on()

        if clockwise:
            self.dir_pin.value(0)
        else:
            self.dir_pin.value(1)

        for _ in range(self.STEPS_PER_REV):
            self.step_pin.value(1)
            utime.sleep_us(delay)
            self.step_pin.value(0)
            utime.sleep_us(delay)

        utime.sleep_ms(1)  # 消除惯性

        self.off()
