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

MM_DIR = r'D:\python_code\micro_manager\Micro-Manager-2.0gamma'
CFG_DIR = r'./cfg_folder'
sys.path.insert(0, MM_DIR)

import pymmcore

# […]
#%%

core = pymmcore.CMMCore()
core.setDeviceAdapterSearchPaths([MM_DIR])
core.loadSystemConfiguration(os.path.join(CFG_DIR, 'MMConfig_demo.cfg'))

