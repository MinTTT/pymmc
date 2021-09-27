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

MM_DIR = r'G:\CP_ZJW\Micro-Manager-2.0gamma'
CFG_DIR = r'./cfg_folder'
sys.path.insert(0, MM_DIR)

import pymmcore

# […]
#%%

core = pymmcore.CMMCore()
core.setDeviceAdapterSearchPaths([MM_DIR])
core.loadSystemConfiguration(r'./cfg_folder/iSynBio_MMConfig_TI_ORCA_sync_exposure_no_xystage.cfg')

