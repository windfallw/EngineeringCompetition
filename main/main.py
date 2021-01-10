from py.hcsr04 import HCSR04
from py.us100 import US100UART
from pyb import UART
import _thread
import utime

sensor = HCSR04(trigger_pin='PD9', echo_pin='PD10')
uart = UART(1, 9600)
uart.init(9600, bits=8, parity=None, stop=1)
US = US100UART(uart)


def test04():
    while True:
        try:
            distance = sensor.distance_cm()
            print('HCSR04 Distance:', distance, 'cm')
        except OSError as ex:
            print('ERROR getting distance:', ex)

        utime.sleep_ms(50)


_thread.start_new_thread(test04, ())
