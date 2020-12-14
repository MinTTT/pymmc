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

MM_DIR = r'D:/python_code/micro_manager/Micro-Manager-2.0gamma/'
sys.path.insert(0, MM_DIR)

import pymmcore

# […]
#%%

cmm = pymmcore.CMMCore()
cmm.loadSystemConfiguration(MM_DIR + 'mmc2_ti2_light_path.cfg')