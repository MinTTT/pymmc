# -*- coding: utf-8 -*-

"""
 @auther: Pan M. CHU
"""

# Built-in/Generic Imports
import os
import sys
# […]

# Libs

import numpy as np  # Or any other

MM_DIR = r'C:/Users/TI2/Micro-Manager-2.0gamma/'
CFG_DIR = r'./cfg_folder/'
sys.path.insert(0, MM_DIR)

import pymmcore

# […]
#%%

core = pymmcore.CMMCore()
core.setDeviceAdapterSearchPaths([MM_DIR])
core.loadSystemConfiguration(CFG_DIR + 'mmc_ti2_device.cfg')