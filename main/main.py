from py.hcsr04 import HCSR04
from pyb import UART
import _thread
import utime

sensor = HCSR04(trigger_pin='PD9', echo_pin='PD10')
pi = UART(1, 115200)
pi.init(115200, bits=8, parity=None, stop=1)


def test04():
    while True:
        try:
            if pi.any():
                print(pi.read())
            distance = sensor.distance_cm()
            pi.write(str(distance) + '\r\n')
            print('HCSR04 Distance:', distance, 'cm')
        except OSError as ex:
            print('ERROR getting distance:', ex)
        utime.sleep_ms(50)


_thread.start_new_thread(test04, ())
