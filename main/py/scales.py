from .hx711 import HX711
from utime import sleep_us


class Scales(HX711):
    weight = None

    def __init__(self, d_out, pd_sck, offset=0, rate=1):
        super(Scales, self).__init__(d_out, pd_sck)
        self.offset = offset
        self.calibrate = rate

    def reset(self):
        self.power_off()
        self.power_on()

    def tare(self):
        self.offset = self.read()
        return 'HX711 set offset %s' % self.offset

    def regulate(self, rate):
        """设置校正系数"""
        self.calibrate = rate

    def raw_value(self):
        return self.read() - self.offset

    def stable_value(self, reads=10, delay_us=500):
        """单位g"""
        values = []
        for _ in range(reads):
            values.append(self.raw_value())
            sleep_us(delay_us)
        self.weight = round(self._stabilizer(values) * self.calibrate / 1000)

    @staticmethod
    def _stabilizer(values, deviation=10):
        weights = []
        # 偏差倍数小于10倍则对应数的权值+1
        for prev in values:
            if prev:
                weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
        # zip将数值和其权值打包成元组，sorted以后取权值最大的数
        return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]
