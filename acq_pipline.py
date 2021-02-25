# -*- coding: utf-8 -*-

"""
 @author: Pan M. CHU
"""

# Built-in/Generic Imports
import os
import sys
# […]

# Libs
import pandas as pd
import numpy as np  # Or any other
# […]

# Own modules
from multi_t_xy_c_acquisiation import multi_acq_3c
import _thread as thread
from valve.pymm_valve import valve_control


#%%
DIR = './test'
POSITION_FILE = './cfg_folder/multipoints.xml'
MICROSCOPE = 'Ti2E'  # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ
time_step = [0, 2, 0]  # [hr, min, s]
flu_step = 0  # very 4 phase loops acq if 0, don't acq a flu channel
time_duration = [24, 0, 0]

valve_control('come4', 0)

acqisition = [True]
thread.start_new_thread(multi_acq_3c, (DIR, POSITION_FILE, MICROSCOPE, time_step, flu_step, time_duration, acqisition))
