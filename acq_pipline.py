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
from multi_t_xy_c_acquisiation import PymmAcq
from valve.pymm_valve import ValveController


#%%
MICROSCOPE = 'Ti2E'  # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ
DIR = './test'
POSITION_FILE = './cfg_folder/multipoints.xml'
time_step = [0, 2, 0]  # [hr, min, s]
flu_step = 0  # very 4 phase loops acq if 0, don't acq a flu channel
time_duration = [24, 0, 0]

acq_loop = PymmAcq(device=MICROSCOPE)
val_contr = ValveController(port='com4')
acq_loop.multi_acq_3c(DIR, POSITION_FILE, time_step, flu_step, time_duration)

# if want to stop acq loop
# acq_loop.stop_acq_loop()

# if want control valve
# val_contr.valve_on()  # open valve
# val_contr.valve_off()  # close valve