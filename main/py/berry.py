from pyb import UART
import collections
import binascii
import json


class RaspberryPi:
    rx_raw_line = b''
    tx_raw_line = b''

    rx_split = b'#'
    tx_split = b'*'

    us100 = collections.OrderedDict()
    us100['us1'] = None
    us100['us2'] = None
    us100['us3'] = None
    us100['us4'] = None

    data = collections.OrderedDict()
    data['us100'] = us100
    data['scale'] = None
    data['offset'] = None
    data['hall'] = None

    result = {'code': 401, 'data': {}, 'msg': ''}
    task = {
        'id': None,
        'result': result
    }

    def __init__(self, port):
        self.uart = UART(port, 115200)  # TX PA9 RX PA10
        self.uart.init(115200, bits=8, parity=None, stop=1, timeout=0)

    def __repr__(self):
        return 'stm32 & RaspberryPi Communication via Uart'

    def writeline(self, data):
        result = json.dumps(data).encode('utf-8', 'strict')
        self.tx_raw_line = b'%s%s%d\r\n' % (result, self.tx_split, binascii.crc32(result))
        self.uart.write(self.tx_raw_line)

    def write_task_result(self):
        self.writeline(data=self.task)

    def parseData(self, data):
        if 'id' and 'func' and 'kwargs' in data:

            if self.task['id'] == data['id']:
                self.write_task_result()

            else:
                self.result.clear()
                self.task['id'] = data['id']
                return data['func'], data['kwargs']

    def readline(self):
        if self.uart.any():
            self.rx_raw_line = self.uart.readline()

            if self.rx_raw_line.rfind(self.rx_split) > 0:
                raw = self.rx_raw_line.rsplit(self.rx_split, 1)
                crc32 = int(raw[1].replace(b'\r\n', b''))

                if crc32 == binascii.crc32(raw[0]):
                    result = json.loads(raw[0].decode('utf-8', 'strict'))
                    return self.parseData(result)

                else:
                    raise Exception("crc32 checksum error")

            else:
                raise Exception("uart received an error data")
