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

from functools import partial


# […]

# Own modules


class NIFPGADevice:
    """
    Basic Usage:

    METHOD:

    .busy(): - bool, get the NI_FPGA state, True indicates the device is outputting signals

    .set_exposure() - float, set the exposure time in milliseconds.

    .set_outputpinmap() - bitwise, the output pin for 1-7 DIOs of FPGA that will be triggered simultaneously with camera.

    .get_exposure() - return the exposure time in milliseconds.

    .trigger_one_pulse() - only output one pulse. useful for get a snap.

    .trigger_continuously() - output a pulse sequence, useful for living or acquiring a image sequence.

    .stop_trigger_continuously() - stop continuous trigger, interrupt the living.

    .close() - close the NI_FPGA session.

    PROPERTY:

    NOTime - set or get the pulse width in microseconds.

    OFFTime - set or get the width between two pulse in microseconds.

    FrameRate - set or get the frame rate.

    Synchronization - if True, the light source state dependent on camera trigger out signal.

    """

    def __init__(self, bitfile: str = r'device/NI_FPGA/myRIO_v4.lvbitx',
                 resource: str = 'rio://172.22.11.2/RIO0'):
        """
        Initial the NI_FPGA session:
        :param bitfile: string, bitfile location.
        :param resource: string an already open session
        """
        self.bifile = bitfile
        self.resource = resource
        self.fpga_session = None  # type: Optional[Session]
        self.register_names = []  # type: List[str]
        self.register_values = dict()  # type: dict

        self._PulseNumber = None  # type: Optional[int]

        self._trigger_value = 1  # type: int
        self._block_TTL = True  # type: bool
        self._TTL_on = False  # type: bool

        self._FPS = None  # type: Optional[float]
        self._cycle_time = None  # type: Optional[float]
        self._FPSLimit = 40.  # type: float
        self._ReadOutTimeLimit = 1360  # type: int # microsecond
        self._DefaultPulseNumber = 1  # type: Optional[int]
        self._trigger = None  # type: Optional[Callable]
        self._sync = None  # type: Optional[bool]
        self._sequence = False
        self._OutputPinMap = 0
        self._breakinloop = False
        self._trigger = 0
        self._PinArray = [0, 0, 0, 0, 0, 0, 0, 0]
        self._SequenceSize = 0
        self._ONTime = None  # type: Optional[int] # unit: microsecond
        self._OFFTime = None  # type: Optional[int] # unit: microsecond

        self._DefaultParameters = {'PulseNumberperLoop': [self._PulseNumber, 1],
                                   'BreakinLoop': [self._breakinloop, True],
                                   'Trigger': [self._trigger, 0],
                                   'OFFTime': [self._OFFTime, 20000],
                                   'ONTime': [self._ONTime, 30000],
                                   'OutputPinMap': [self._OutputPinMap, 0],
                                   'Synchronization': [self._sync, True],
                                   'Sequence': [self._sequence, False],
                                   'SequenceSize': [self._SequenceSize, 0],
                                   'PinArray': [self._PinArray, [0, 0, 0, 0, 0, 0, 0, 0]]
                                   }

        # init device
        self.open_session()
        self.fpga_session.registers['PulseNumberperLoop'].write(self._DefaultPulseNumber)
        self.get_register_values()
        self.initialMyRIO()

    def __del__(self):
        for key, values in self._DefaultParameters.items():
            self.fpga_session.registers[key].write(values[-1])
        self.close()

    def initialMyRIO(self):
        for key, values in self._DefaultParameters.items():
            self.fpga_session.registers[key].write(values[-1])
        self.stop_trigger_continuously()
        return None

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
        self._OutPutPinMap = self.register_values['OutputPinMap']
        self._sync = self.register_values['Synchronization']

    def get_prop(self, prop_name):
        attr_name = self._DefaultParameters[prop_name][0]
        self.__dict__[attr_name] = self.register_reader(prop_name)
        return self.__dict__[attr_name]

    def set_prop(self, prop_name, value):
        attr_name = self._DefaultParameters[prop_name][0]
        self.__dict__[attr_name] = value
        self.register_writer(prop_name)

    def del_prop(self, prop_name):
        attr_name = self._DefaultParameters[prop_name][0]
        del self.__dict__[attr_name]

    #
    # def initProperty(self):
    #     for key, value in self._DefaultParameters.items():
    #         self.__dict__[key] = property(partial(self.get_prop, key),
    #                                             partial(self.set_prop, key),
    #                                             partial(self.del_prop, key))

    def register_reader(self, name: str):
        return self.fpga_session.registers[name].read()

    def register_writer(self, name, value):
        self.fpga_session.registers[name].write(value)

    def busy(self) -> bool:
        if self.fpga_session.registers['Trigger'].read() != 0:
            return True
        else:
            return False

    @property
    def PinArray(self):
        self._PinArray = self.register_reader('PinArray')
        return self._PinArray

    @PinArray.setter
    def PinArray(self, pinArray: list):
        for i in range(len(pinArray)):
            pinArray[i] = np.uint8(pinArray[i])
        self._PinArray = pinArray
        self.register_writer('PinArray', self._PinArray)

    @property
    def OutPutPinMap(self):
        self._OutputPinMap = self.register_reader('OutputPinMap')
        return self._OutputPinMap

    @OutPutPinMap.setter
    def OutPutPinMap(self, map: int):
        self._OutputPinMap = map
        self.register_writer('OutputPinMap', np.uint8(map))

    @property
    def Synchronization(self):
        self._sync = self.register_reader('Synchronization')
        return self._sync

    @Synchronization.setter
    def Synchronization(self, state: bool):
        self._sync = state
        self.register_writer('Synchronization', state)

    @property
    def Sequence(self):
        self._sequence = self.register_reader('Sequence')
        return self._sequence

    @Sequence.setter
    def Sequence(self, value):
        self._sequence = value
        self.register_writer('Sequence', value)

    @property
    def SequenceSize(self):
        self._SequenceSize = self.register_reader('SequenceSize')
        return self._SequenceSize

    @SequenceSize.setter
    def SequenceSize(self, value: int):
        self._SequenceSize = value
        self.register_writer('SequenceSize', value)

    @property
    def ONTime(self):
        self._ONTime = self.fpga_session.registers['ONTime'].read()
        return self._ONTime

    @ONTime.setter
    def ONTime(self, time: int):
        """
        NOTime - set or get the pulse width in microseconds.
        :param time: microseconds
        """
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

    def set_exposure(self, time: float):
        """
        set the exposure time
        :param time: float, unit is millisecond.
        :return:
        """
        self.ONTime = int(time * 1000)

    def set_outputpinmap(self, pin_map: int):
        """Set the Connector C DIO 1-7 output mode.

        Parameters
        ---------------
        pin_map : int
            Connector C DIO 1-7 are mapped to its bitwise value. 

        """
        self.OutPutPinMap = pin_map

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
        self.fpga_session.registers['BreakinLoop'].write(False)
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
        """
        self.initialMyRIO()
        self.fpga_session.close()


# %%
if __name__ == '__main__':
    # %%
    ni_fpga = NIFPGADevice(bitfile=r'device/NI_FPGA/myRIO_v6.lvbitx', resource='rio://172.22.11.2/RIO0')
