import serial
import struct
from typing import Union
COM_PORT = 'com7'



# values = (8,)
# # values = (2,)
# data = struct.pack('!{0}B'.format(len(values)), *values)
# ser.write(data)
# ret = ser.read(10)
# print(struct.unpack(f'!{len(ret)}B', ret))


class ARDUINO:
    def __init__(self, com='COM7', baud=57600, time_out=0.01):
        if com is None:
            raise ValueError('No COM port')
        self.com_port = com
        self.baud = baud
        self.time_out = time_out
        self._trigger_pattern = None
        self.ret = None
        self._series = None  # type: serial.Serial

        self.connect()

    @property
    def trigger_pattern(self):
        return self._trigger_pattern

    @trigger_pattern.setter
    def trigger_pattern(self, pattern):
        self._trigger_pattern = pattern
        self.cmd((1, self._trigger_pattern))

    def get_current_pattern(self):
        self.cmd((2, ))
        return self.ret[1:]

    def connect(self):
        self._series = serial.Serial(self.com_port, self.baud, timeout=self.time_out)

    def cmd(self, code):
        if not isinstance(code, tuple):
            code = (code, )
        command = struct.pack('!{0}B'.format(len(code)), *code)
        _ = self._series.write(command)
        rets = self._series.read(10)
        self.ret = struct.unpack(f'!{len(rets)}B', rets)

    def start_trigger_mode(self):
        self.cmd((8, ))

    def stop_trigger_mode(self):
        self.cmd((9, ))

    def start_blanking_mode(self):
        self.cmd(20)

    def stop_blanking_mode(self):
        self.cmd(21)

    def blanking_positive(self, state=True):
        if state:
            self.cmd((22, 0))
        else:
            self.cmd((22, 1))

    def close_session(self):
        self._series.close()

#%%
if __name__ == '__mian__':
    arduino = ARDUINO('COM7')
    arduino.trigger_pattern = 0b00110000
    arduino.start_blanking_mode()