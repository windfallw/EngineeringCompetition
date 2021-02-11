from pyb import UART
import collections
import binascii
import utime
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
    data['hall'] = None

    current_task_id = None
    current_task_status = None
    current_task_msg = ''
    current_task_data = {}

    current_task_info = collections.OrderedDict()

    def __init__(self, port):
        self.uart = UART(port, 115200)  # TX PA9 RX PA10
        self.uart.init(115200, bits=8, parity=None, stop=1, timeout=0)
        utime.sleep_ms(500)  # 没加延迟开机以后读的数据会乱

    def __repr__(self):
        return 'stm32 & RaspberryPi Communication via Uart'

    def writeline(self, data=None):
        """传入dict，将其转换为二进制json字符串并发送"""
        if data is None:
            data = self.data
        result = json.dumps(data).encode('utf-8', 'strict')
        self.tx_raw_line = b'%s%s%d\r\n' % (result, self.tx_split, binascii.crc32(result))
        self.uart.write(self.tx_raw_line)

    def write_task_result(self):
        """发送任务完成情况"""
        self.current_task_info['id'] = self.current_task_id
        self.current_task_info['status'] = self.current_task_status
        self.current_task_info['msg'] = self.current_task_msg
        self.current_task_info['data'] = self.current_task_data
        self.writeline(data=self.current_task_info)

    def parseData(self, data):
        """准备执行任务"""
        if 'id' and 'func' and 'kwargs' in data:
            if self.current_task_id is not data['id']:
                # 接收新任务并重置状态。
                self.current_task_id = data['id']
                self.current_task_status = False
                self.current_task_msg = 'executing...'
                self.current_task_data.clear()
                return data['func'], data['kwargs']
            else:
                # 重复接收到相同任务时。说明stm32执行任务结束后所发送的信息，pi可能接收失败了或暂时未接收到，那就在发送一次。
                # 还有一种特例是树莓派脚本重启了，若上次执行的id刚好到0为止的话，第一次命令就不会执行了。
                # 因此树莓派脚本首次运行时应当发送个重置id指令。
                self.write_task_result()

    def readline(self):
        """读取树莓派传输的数据"""
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
