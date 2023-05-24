import os
import sys
import time

import numpy as np
# from pycromanager import Acquisition, multi_d_acquisition_events
import pycromanager
import tifffile as tiff
import threading as thread
from device.arduino import ARDUINO
import h5py
from typing import Callable
from pycromanager import Bridge
from pycromanager import Core
from pycromanager import Studio
from device.NI_FPGA import NIFPGADevice
from typing import Optional, Callable

thread_lock = thread.Lock()
bridge = Bridge()
global core
core = Core()

studio = Studio()


# %%

def javaList(strVector):
    return [strVector.get(i) for i in range(strVector.size())]


class mmDevice(object):
    device_name = None
    MMCore = None

    def __init__(self, device_name: str, mmCore: pycromanager.Core):
        self.device_name = device_name
        self.mmCore = mmCore
        self.property_list = self.__getDeviceProperties()
        self.property_dict = self.__getPropertiesValue()
        self.allowed_property_value = self.__getAllAllowedProVal()

    def __getDeviceProperties(self):
        return javaList(self.mmCore.get_device_property_names(self.device_name))

    def __getPropertiesValue(self):
        return {pro_name: core.get_property(self.device_name, pro_name) for pro_name in self.property_list}

    def __getAllAllowedProVal(self):
        return {pro_name: javaList(core.get_allowed_property_values(self.device_name, pro_name))
                for pro_name in self.property_list}

    def get_property(self, propertyName: str):
        self.property_dict = self.__getPropertiesValue()
        return self.property_dict[propertyName]

    def set_property(self, propertyName, propertyValue):
        allowed_value = self.allowed_property_value[propertyName]
        if not allowed_value:
            if propertyValue not in allowed_value:
                raise ValueError(f'Allowed values for device {self.device_name} are {allowed_value}.')
        self.mmCore.set_property(self.device_name, propertyName, propertyValue)


# %%
camera = mmDevice(core.get_camera_device(), core)
disp = studio.live()
disp.set_live_mode_on(True)

ni_fpga = NIFPGADevice(bitfile=r'device/NI_FPGA/myRIO_v5.lvbitx', resource='rio://172.22.11.2/RIO0')

ni_fpga.set_exposure(10)
ni_fpga.trigger_continuously()