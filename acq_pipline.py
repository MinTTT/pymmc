"""
 @author: Pan M. CHU
"""

# Built-in/Generic Imports
# Own modules
import os
from multi_t_xy_c_acquisiation import PymmAcq
from device.valve.pymm_valve import ValveController

# %%
MICROSCOPE = 'TiE_prior'  # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ, TiE_prior, Ti2E_LDJ
DIR = r'I:\20210906'
# POSITION_FILE = r'H:\Image_Data\moma_data\20210505_pECJ3_M5_L3\multipoints.xml'
POSITION_FILE = None
acq_loop = PymmAcq(device=MICROSCOPE)
device_cfg = acq_loop.device_cfg
# device_cfg.set_ROI([0, 710, 2048, 1024])
# device_cfg.set_ROI([0, 0, 2048, 2048])
device_cfg.set_ROI([0, 812, 2048, 820])

device_cfg.prior_core.set_filter_speed_acc(100, 100, 1)
device_cfg.set_light_path('BF', '60X', shutter=device_cfg.SHUTTER_LAMP)
device_cfg.set_device_state(shift_type='init_phase')
# %%
# acq_loop.nd_recorder.export_pos(DIR)
acq_loop.nd_recorder.import_pos(os.path.join(DIR, 'pos.jl'))

acq_loop.open_NDUI()

# %%
time_step = [0, 3, 0]  # [hr, min, s]
flu_step = 4  # very 4 phase loops acq if 0, don't acq a flu channel
time_duration = [72, 0, 0]

acq_loop.multi_acq_3c(DIR, POSITION_FILE, time_step, flu_step, time_duration)

# if want to stop acq loop
# acq_loop.stop_acq_loop()

# %%
val_contr = ValveController(port='com9')
# val_contr.valve_off()
# if want control valve

val_contr.valve_off()  # close valve
val_contr.valve_on()  # open valve
# device_cfg.mmcore.start_continuous_sequence_acquisition(10)
# device_cfg.mmcore.stop_sequence_acquisition()
# import numpy as np
# from tqdm import tqdm
# from joblib import Parallel, delayed
#
# vedio = np.random.random((device_cfg.mmcore.get_remaining_image_count(), 2048, 2048))
# tags = [None] * len(vedio)
#
#
# def parall_output(i):
#     tagged_image = device_cfg.mmcore.pop_next_tagged_image()
#     vedio[:, ...] = np.reshape(tagged_image.pix, [tagged_image.tags["Height"], tagged_image.tags["Width"]])
#     tags[i] = tagged_image.tags
#
#
# _ = Parallel(n_jobs=1, require='sharedmem')(delayed(parall_output)(i) for i in tqdm(range(len(vedio))))
# # for i in tqdm(range(len(vedio))):
# #     tagged_image = device_cfg.mmcore.pop_next_tagged_image()
# #     vedio[:, ...] = np.reshape(tagged_image.pix, [tagged_image.tags["Height"], tagged_image.tags["Width"]])
# #     tags[i] = tagged_image.tags
# vedio = vedio.astype(np.uint16)
# import pymm
#
# pymm.save_image(vedio, r'./cfg_folder/test', 'vedio', meta={'tag_data': tags})
