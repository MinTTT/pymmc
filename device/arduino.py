# %%

import serial  # pyserial
import struct
from typing import Union, Optional
import numpy as np
import warnings
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

    @property
    def OutPutPinMap(self):
        return self._trigger_pattern

    @OutPutPinMap.setter
    def OutPutPinMap(self, pattern):
        self._trigger_pattern = pattern
        self.cmd((1, self._trigger_pattern))

    def get_current_pattern(self):
        self.cmd((2, ))
        return self.ret[1:]

    def connect(self):
        self._series = serial.Serial(
            self.com_port, self.baud, timeout=self.time_out)

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

    def trigger(self, map=None):
        """
        This method trigger the port 4 in arduino. It used to trigger camera when it sates in external trigger mode.

        :return:
        """
        if map:
            self.trigger_pattern = map
        self.cmd((3,))

    def close_session(self):
        self._series.close()

    def trigger_continuously(self):
        self.cmd((4,))

    def stop_trigger_continuously(self):
        self.cmd((3,))

    def trigger_one_pulse(self):
        self.cmd((3,))

    @property
    def ONTime(self):
        return 1

    @ONTime.setter
    def ONTime(self, time):
        pass

    @property
    def OFFTime(self):
        return 1

    @OFFTime.setter
    def OFFTime(self, time):
        pass


class TriggerArduinoDue:
    def __init__(self, com='COM13', baud=9600, time_out=0.01):
        if com is None:
            raise ValueError('No COM port')
        self.com_port = com
        self.baud = baud
        self.time_out = time_out
        self._trigger_pattern = None
        self.ret: Optional[list] = None  # type: Optional[list]

        self._series = None  # type: Optional[serial.Serial]
        self._ONTime = 27000
        self._OFFTime = 20000
        
        self._FPS = None  # type: Optional[float]
        self._cycle_time = None  # type: Optional[float]
        self._FPSLimit = 40.  # type: float
        self._ReadOutTimeLimit = 1360  # type: int # microsecond
        self._DefaultPulseNumber = 1  # type: Optional[int]
        self._trigger = None  # type: Optional[Callable]
        self._sync = None  # type: Optional[bool]

        self.connect()
        print(f'TriggerArduinoDue -> Connection success.')

    @property
    def trigger_pattern(self):
        return self._trigger_pattern

    @trigger_pattern.setter
    def trigger_pattern(self, pattern):
        self._trigger_pattern = pattern
        self.cmd((1, self._trigger_pattern))

    @property
    def OutPutPinMap(self):
        return self._trigger_pattern

    @OutPutPinMap.setter
    def OutPutPinMap(self, pattern):
        self._trigger_pattern = pattern
        self.cmd((1, self._trigger_pattern))

    def get_current_pattern(self):
        self.cmd((2, ))
        return self.ret[1:]

    @property
    def ONTime(self):
        return self._ONTime

    @ONTime.setter
    def ONTime(self, time):
        """
        """
        self._set_ONOFFTime(time, self._OFFTime)

    @property
    def OFFTime(self):
        return self._OFFTime

    @OFFTime.setter
    def OFFTime(self, time):
        self._set_ONOFFTime(self._ONTime, time)
        
        
    
    @property
    def FrameRate(self):
        """
        Frame rate, frames/s.
        :return:
        """
        self._cycle_time = self.ONTime + self.OFFTime
        try:
            self._FPS = 1E6 / self._cycle_time
            return self._FPS
        except ZeroDivisionError:
            self._FPS = np.nan
            warnings.warn('One Cycle is Zero!')

    @FrameRate.setter
    def FrameRate(self, fps: float):
        """
        Dhyana 400 BSI V2, the Frame rate < 40 is safe, and the raw period is 6.6 us.
        1. Standard Mode, Exposure Mode - Timed, the exposure time is dependent to software setting.
        2. Standard Mode, Exposure Mode - Width, the exposure time is dependent to pulse width.
        3. Synchronization. The exposure time dependent to pulse cycle. ON time + OFF time is the exposure time.

        For the safety reason, the OFF time is not allowed to be set to lower than 1360 microseconds.
        :param fps:
        :return:
        """
        if fps > self._FPSLimit:
            warnings.warn(f"The frame rate is extend to the current limit ({self._FPSLimit}).")
            fps = self._FPSLimit
        cycle_time = 1E6 / fps
        desired_off_time = cycle_time - self.ONTime
        if desired_off_time < self._ReadOutTimeLimit:
            self.ONTime = int(cycle_time - self._ReadOutTimeLimit)
            self.OFFTime = self._ReadOutTimeLimit
            warnings.warn(f'Need more time for image reading out, the exposure time is set to '
                          f'{"%.2f" %(self._ONTime / 1000)} ms.')
        else:
            self.OFFTime = int(desired_off_time)

    def connect(self):
        self._series = serial.Serial(
            self.com_port, self.baud, timeout=self.time_out)

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

    def _set_ONOFFTime(self, ONtime: Optional[int] = None,
                       OFFtime: Optional[int] = None):
        """
        Time in ns.
        """
        if ONtime:
            self._ONTime = int(ONtime)
        if OFFtime:
            self._OFFTime = int(OFFtime)
        command = struct.pack('!1B2L', *(6, self._ONTime, self._OFFTime))
        _ = self._series.write(command)

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

    def trigger(self, map=None):
        """
        This method trigger the port 4 in arduino. It used to trigger camera when it sates in external trigger mode.

        :return:
        """
        if map:
            self.trigger_pattern = map
        self.cmd((3,))

    def close_session(self):
        self._series.close()

    def stop_trigger_continuously(self):
        self.cmd((5,))

    def trigger_continuously(self,
                             triggerNumber: Optional[int] = None):
        if triggerNumber is None:
            self.cmd((4,))
        else:
            command = struct.pack('!1B1L', *(7, int(triggerNumber)))
            _ = self._series.write(command)

    def trigger_one_pulse(self):
        self.cmd((3,))


# %%
if __name__ == '__mian__':
    # %%
    import time
    arduino = TriggerArduinoDue()
    arduino.stop_trigger_continuously()
    # arduino.cmd(1)
    arduino.ONTime = 35000
    arduino.trigger_continuously()
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
