"""
 @author: Pan M. CHU
"""

# Built-in/Generic Imports
# Own modules
import os
import time

from multi_t_xy_c_acquisiation import PymmAcq
from device.valve.pymm_valve import ValveController

# %%
MICROSCOPE = 'TiE_prior_DNA_replicate'  # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ, TiE_prior, Ti2E_LDJ
DIR = r'F:\zjw\20211203_HWQ'
# POSITION_FILE = r'H:\Image_Data\moma_data\20210505_pECJ3_M5_L3\multipoints.xml'
POSITION_FILE = None
acq_loop = PymmAcq(device=MICROSCOPE)
device_cfg = acq_loop.device_cfg

# device_cfg.set_ROI([0, 710, 2048, 1024])
# device_cfg.set_ROI([0, 0, 2048, 2048])
device_cfg.set_ROI([0, 812, 2048, 820])
device_cfg.set_device_state(shift_type='init_phase')
# device_cfg.prior_core.set_filter_speed_acc(100, 100, 1)


# %%
# acq_loop.nd_recorder.export_pos(DIR)
acq_loop.nd_recorder.import_pos(os.path.join(DIR, 'pos.jl'))

acq_loop.open_NDUI()

# %%
time_step = [0, 3, 0]  # [hr, min, s]
flu_step = 1  # very 4 phase loops acq if 0, don't acq a flu channel
time_duration = [72, 0, 0]
device_cfg.set_light_path('BF', '100X_External')
device_cfg.set_device_state(shift_type='init_phase')
acq_loop.multi_acq_2c(DIR, POSITION_FILE, time_step, flu_step, time_duration)

# if want to stop acq loop
# acq_loop.stop_acq_loop()

# %%
val_contr = ValveController(port='com9')
# val_contr.valve_off()
# if want control valve

val_contr.valve_off()  # close valve
val_contr.valve_on()  # open valve

# %%





exp_time = 25
device_cfg.set_ROI([0, 812, 2048, 820])
for i in range(200):
    device_cfg.image_grabber.auto_acq_save(r'C:\Users\pc\Desktop\streads\HDR_mode',
                                           f'test{i}.tiff', exposure=exp_time,
                                           shutter=device_cfg.fpga_core.trigger_one_pulse)
    exp_time += 1
    time.sleep(0.1)


import numpy as np
device_cfg.set_ROI([0, 812, 2048, 820])
for i in range(10):
    exp_time = np.random.uniform(25, 200)
    device_cfg.image_grabber.auto_acq_save(r'F:\zjw\20211209_test\Globalresetlow',
                                           f'test{i}', exposure=exp_time,
                                           shutter=device_cfg.fpga_core.trigger_one_pulse)
    time.sleep(0.1)

exp_time = 50
device_cfg.set_ROI([0, 812, 2048, 820])
for i in range(50):
    device_cfg.arduino_core.trigger_pattern = 32
    device_cfg.image_grabber.auto_acq_save(r'C:\Users\pc\Desktop\streads\Two_channel2\phase',
                                           f'test{i}.tiff', exposure=exp_time,
                                           shutter=device_cfg.fpga_core.trigger_one_pulse)
    device_cfg.arduino_core.trigger_pattern = 16
    device_cfg.image_grabber.auto_acq_save(r'C:\Users\pc\Desktop\streads\Two_channel2\yellow',
                                           f'test{i}.tiff', exposure=exp_time,
                                           shutter=device_cfg.fpga_core.trigger_one_pulse)
    exp_time += 5
    time.sleep(0.1)