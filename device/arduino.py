#%%
import serial  # pyserial
import struct
from typing import Union, Optional
# values = (8,)
# # values = (2,)
# data = struct.pack('!{0}B'.format(len(values)), *values)
# ser.write(data)
# ret = ser.read(10)
# print(struct.unpack(f'!{len(ret)}B', ret))


class ARDUINO:
    def __init__(self, com='COM7', baud=9600, time_out=0.01):
        if com is None:
            raise ValueError('No COM port')
        self.com_port = com
        self.baud = baud
        self.time_out = time_out
        self._trigger_pattern = None
        self.ret = None  # type: Optional[list]

        self._series = None  # type: Optional[serial.Serial]

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

    def cmd(self, code: Union[int, tuple]):
        """
        sent bytes to arduino series, input int or Tuple[int].
        :param code: int or tuple
        :return: None
        """
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

    def trigger(self, map=0b10000000):
        """
        This method trigger the port 4 in arduino. It used to trigger camera when it sates in external trigger mode.

        :return:
        """
        
        self.cmd((3, int(map)))

    def close_session(self):
        self._series.close()

#%%
if __name__ == '__mian__':
#%%
    import time
    arduino = ARDUINO('COM12')
    from math import floor
    arduino.trigger_pattern = 0b10000001
    arduino.start_blanking_mode()
    arduino.trigger()
    # arduino.cmd(1)


    # while True:
    #     exposure = 21

    #     freq = floor(1000/exposure)  # req
    #     if freq < 200:
    #         cycle_time = 1000./freq
    #         off_duty_cycle = cycle_time - exposure
    #         one_step_time = cycle_time / 255.
    #         on_step_num = 255 - int(off_duty_cycle / one_step_time)  # intensity
    #     else:
    #         freq = 200
    #         cycle_time = 1000./freq
    #         off_duty_cycle = cycle_time - exposure
    #         one_step_time = cycle_time / 255.
    #         on_step_num = 255 - int(off_duty_cycle / one_step_time)  # intensity


    #     real_time = one_step_time * on_step_num
    #     print(real_time, freq, on_step_num)
    #     arduino.cmd((2, freq, on_step_num))
    #     time.sleep(0.01)


# %%
