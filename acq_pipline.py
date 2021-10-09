"""
 @author: Pan M. CHU
"""

# Built-in/Generic Imports
# Own modules
import os
from multi_t_xy_c_acquisiation import PymmAcq
from device.valve.pymm_valve import ValveController

# %%
MICROSCOPE = 'TiE_prior_arduino'  # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ, TiE_prior, Ti2E_LDJ
DIR = r'F:\zjw\20211007_NH2_pECJ3_M5_L3_updownshift'
# POSITION_FILE = r'H:\Image_Data\moma_data\20210505_pECJ3_M5_L3\multipoints.xml'
POSITION_FILE = None

acq_loop = PymmAcq(device=MICROSCOPE)
device_cfg = acq_loop.device_cfg
device_cfg.set_ROI([0, 812, 2048, 820])

device_cfg.set_device_state(shift_type='init_phase')
# device_cfg.prior_core.set_filter_speed_acc(100, 100, 1)
# device_cfg.set_ROI([0, 710, 2048, 1024])
# device_cfg.set_ROI([0, 710, 2048, 1024])
# device_cfg.set_ROI([0, 0, 2048, 2048])

# %%
# acq_loop.nd_recorder.export_pos(DIR)
acq_loop.nd_recorder.import_pos(os.path.join(DIR, 'pos.jl'))

acq_loop.open_NDUI()

# %%

device_cfg.set_light_path('BF', '60X_External')

# time_step = [0, 3, 30]  # [hr, min, s] in fast growth rate
time_step = [0, 3, 30]  # [hr, min, s] in slow growth rate
flu_step = 6  # very 6 phase loops acq if 0, don't acq a flu channel
time_duration = [72, 0, 0]

acq_loop.multi_acq_3c_sync_light(DIR, POSITION_FILE, time_step, flu_step, time_duration)

# if want to stop acq loop
# acq_loop.stop_acq_loop()

# %%
val_contr = ValveController(port='com9')
# val_contr.valve_off()
# if want control valve

val_contr.valve_off([0, 10, 0])  # close valve
# val_contr.valve_on([2, 30, 0])  # open valve
