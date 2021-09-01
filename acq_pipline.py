
"""
 @author: Pan M. CHU
"""

# Built-in/Generic Imports
# Own modules
from multi_t_xy_c_acquisiation import PymmAcq
from device.valve.pymm_valve import ValveController

#%%
MICROSCOPE = 'TiE_prior'  # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ, TiE_prior, Ti2E_LDJ
DIR = r'H:\Image_Data\moma_data\20210505_pECJ3_M5_L3'
POSITION_FILE = r'H:\Image_Data\moma_data\20210505_pECJ3_M5_L3\multipoints.xml'
acq_loop = PymmAcq(device=MICROSCOPE)
device_cfg = acq_loop.device_cfg
# device_cfg.set_ROI([0, 710, 2048, 1024])
device_cfg.set_ROI([0, 0, 2048, 2048])

# device_cfg.autofocus()
#%%
time_step = [0, 12, 0]  # [hr, min, s]
flu_step = 1  # very 4 phase loops acq if 0, don't acq a flu channel
time_duration = [24, 0, 0]

acq_loop.multi_acq_3c(DIR, POSITION_FILE, time_step, flu_step, time_duration)

# if want to stop acq loop
# acq_loop.stop_acq_loop()

#%%
# val_contr = ValveController(port='com4')
# val_contr.valve_off()
# if want control valve
# val_contr.valve_on()  # open valve
# val_contr.valve_off()  # close valve