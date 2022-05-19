# -*- coding: utf-8 -*-

"""

 @author: Pan M. CHU
 @Email: pan_chu@outlook.com
"""

# Built-in/Generic Imports
import os
import sys
# […]
from nifpga import Session
# Libs
import pandas as pd
import numpy as np  # Or any other
from typing import Optional, List, Callable
import warnings


# […]

# Own modules


class NIFPGADevice:
    """
    Basic Usage:

    METHOD:

    .busy(): - bool, get the NI_FPGA state, True indicates the device is outputting signals

    .set_exposure() - float, set the exposure time in milliseconds.

    .get_exposure() - return the exposure time in milliseconds.

    .trigger_one_pulse() - only output one pulse. useful for get a snap.

    .trigger_continuously() - output a pulse sequence, useful for living or acquiring a image sequence.

    .stop_trigger_continuously() - stop continuous trigger, interrupt the living.

    .close() - close the NI_FPGA session.

    PROPERTY:

    NOTime - set or get the pulse width in microseconds.

    OFFTime - set or get the width between two pulse in microseconds.

    FrameRate - set or get the frame rate.

    """
    def __init__(self, bitfile: str=r'device/NI_FPGA/myRIO_v2.lvbitx',
                 resource: str='rio://172.22.11.2/RIO0'):
        """
        Initial the NI_FPGA session
        :param bitfile: string, bitfile location.
        :param resource: string an already open session
        """
        self.bifile = bitfile
        self.resource = resource
        self.fpga_session = None  # type: Optional[Session]
        self._ONTime = None  # type: Optional[int] # unit: microsecond
        self._OFFTime = None  # type: Optional[int] # unit: microsecond
        self._PulseNumber = None  # type: Optional[int]

        self._trigger_value = 1  # type: int
        self._block_TTL = True  # type: bool
        self._TTL_on = False  # type: bool
        self.register_names = []  # type: List[str]
        self.register_values = dict()  # type: dict
        self._FPS = None  # type: Optional[float]
        self._cycle_time = None  # type: Optional[float]
        self._FPSLimit = 40.  # type: float
        self._ReadOutTimeLimit = 13600  # type: int # microsecond
        self._DefaultPulseNumber = 1  # type: Optional[int]
        self._trigger = None  # type: Optional[Callable]
        self._DefaultParameters = {'PulseNumberperLoop': 1,
                                   'BreakinLoop': False,
                                   'Trigger': 0,
                                   'OFFTime': 15000,
                                   'ONTime': 30000,
                                   'OutputPinMap': 0}
        # init device
        self.open_session()
        self.fpga_session.registers['PulseNumberperLoop'].write(self._DefaultPulseNumber)
        self.get_register_values()
        for key, values in self._DefaultParameters.items():
            self.fpga_session.registers[key].write(values)

    def open_session(self):
        self.fpga_session = Session(self.bifile, self.resource)
        self._trigger = self.fpga_session.registers['Trigger']
        return None

    def get_register_names(self):
        self.register_names = list(self.fpga_session.registers.keys())
        return self.register_names

    def get_register_values(self):
        self.get_register_names()
        self.register_values = {name: self.fpga_session.registers[name].read() for name in self.register_names}
        self._ONTime = self.register_values['ONTime']
        self._OFFTime = self.register_values['OFFTime']
        self._PulseNumber = self.register_values['PulseNumberperLoop']
        self._OutPutPinMap = self.register_values['OutPutPinMap']

    def busy(self) -> bool:
        if self.fpga_session.registers['Trigger'].read() != 0:
            return True
        else:
            return False

    @property
    def ONTime(self):
        self._ONTime = self.fpga_session.registers['ONTime'].read()
        return self._ONTime

    @ONTime.setter
    def ONTime(self, time: int):
        self._ONTime = time
        self.fpga_session.registers['ONTime'].write(time)

    @property
    def OFFTime(self):
        self._OFFTime = self.fpga_session.registers['OFFTime'].read()
        return self._OFFTime

    @OFFTime.setter
    def OFFTime(self, time: int):
        self._OFFTime = time
        self.fpga_session.registers['OFFTime'].write(time)

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

        For the safety reason, the OFF time is not allowed to be set to lower than 13600 microseconds.
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
            warnings.warn('Need more time for image reading out, the exposure time is set to %.2f ms.'
                          % (self._ONTime / 1000))
        else:
            self.OFFTime = int(desired_off_time)

    def set_exposure(self, time: float):
        """
        set the exposure time
        :param time: float, unit is millisecond.
        :return:
        """
        self.ONTime = int(time * 1000)
    
    def set_outputpins(self, pinmap: int):
        

    def get_exposure(self):
        return self.ONTime / 1000.

    def trigger_one_pulse(self):
        while self.busy():
            pass
        self.fpga_session.registers['PulseNumberperLoop'].write(1)
        self._trigger.write(self._trigger_value)
        while self.busy():
            pass
        return None

    def trigger_continuously(self):
        self.fpga_session.registers['PulseNumberperLoop'].write(-1)
        self._trigger.write(self._trigger_value)
        return None

    def stop_trigger_continuously(self):
        self.fpga_session.registers['BreakinLoop'].write(True)
        while self.busy():
            pass
        self.fpga_session.registers['PulseNumberperLoop'].write(self._PulseNumber)
        self.fpga_session.registers['BreakinLoop'].write(False)
        return None

    def close(self):
        """
        Close the session of NI FPGA,
        :return:
        """
        self.fpga_session.close()
        return None


# %%
if __name__ == '__main__':
    # %%
    ni_fpga = NIFPGADevice(bitfile=r'device/NI_FPGA/myRIO_v1.lvbitx', resource='rio://172.22.11.2/RIO0')
