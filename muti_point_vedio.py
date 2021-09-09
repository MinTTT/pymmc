import os
from multi_t_xy_c_acquisiation import PymmAcq

MICROSCOPE = 'TiE_prior'  # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ, TiE_prior, Ti2E_LDJ
DIR = r'./cfg_folder/test/'
# POSITION_FILE = r'H:\Image_Data\moma_data\20210505_pECJ3_M5_L3\multipoints.xml'
POSITION_FILE = None
acq_loop = PymmAcq(device=MICROSCOPE)
device_cfg = acq_loop.device_cfg
# device_cfg.set_ROI([0, 710, 2048, 1024])
# %%
device_cfg.set_ROI([0, 0, 2048, 2048])
device_cfg.prior_core.set_filter_speed_acc(100, 100, 1)
device_cfg.set_light_path('BF', '10X', shutter=device_cfg.SHUTTER_LAMP)

device_cfg.mmcore.set_property(device_cfg.mmcore.get_camera_device(), 'Binning', '1x1')
device_cfg.set_device_state(shift_type='init_phase')

duration_time = 2 * 1000  # ms
step = 24.5  # ms

dir = r'./cfg_folder/test/'
name = 'test'

acq_loop.open_NDUI()

#%%

for index, fov in enumerate(acq_loop.nd_recorder):
    acq_loop.go_to_position(index)
    acq_loop.continuous_acq(duration_time, step, os.path.join(dir, f'{name}_xy_{index+1}.tiff'))
