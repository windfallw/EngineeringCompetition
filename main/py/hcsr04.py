from machine import Pin
import machine
import utime


class hcsr04:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)
        self.trigger.value(0)

    def _send_pulse_and_wait(self):
        self.trigger.value(1)
        utime.sleep_us(50)
        self.trigger.value(0)

        try:
            pulse_time = machine.time_pulse_us(self.echo, 1)
            return pulse_time

        except Exception as err:
            print(err)

    def distance(self):
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2 
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.034320 cm/us that is 1cm each 29.1us
        cms = (pulse_time / 2) / 29.1
        return cms
