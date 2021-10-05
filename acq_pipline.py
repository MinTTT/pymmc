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
DIR = r'G:\CP_ZJW\pymmc\cfg_folder\test'
# POSITION_FILE = r'H:\Image_Data\moma_data\20210505_pECJ3_M5_L3\multipoints.xml'
POSITION_FILE = None

acq_loop = PymmAcq(device=MICROSCOPE)
device_cfg = acq_loop.device_cfg
device_cfg.set_ROI([0, 812, 2048, 820])
device_cfg.set_device_state(shift_type='init_phase')
device_cfg.prior_core.set_filter_speed_acc(100, 100, 1)
# device_cfg.set_ROI([0, 710, 2048, 1024])
# device_cfg.set_ROI([0, 710, 2048, 1024])
# device_cfg.set_ROI([0, 0, 2048, 2048])

# %%
# acq_loop.nd_recorder.export_pos(DIR)
acq_loop.nd_recorder.import_pos(os.path.join(DIR, 'pos.jl'))

acq_loop.open_NDUI()

# %%

device_cfg.set_light_path('BF', '100X_External')

time_step = [0, 0, 5]  # [hr, min, s]
flu_step = 1  # very 4 phase loops acq if 0, don't acq a flu channel
time_duration = [72, 0, 0]

acq_loop.multi_acq_3c_sync_light(DIR, POSITION_FILE, time_step, flu_step, time_duration)

# if want to stop acq loop
# acq_loop.stop_acq_loop()

# %%
val_contr = ValveController(port='com9')
# val_contr.valve_off()
# if want control valve

val_contr.valve_off()  # close valve
val_contr.valve_on()  # open valve

# %%
# import time
# _current_t = time.time()
#
# while time.time() - _current_t < 10:
#     print(device_cfg.prior_core.device_busy())

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

# for i in tqdm(range(len(vedio))):
#     tagged_image = device_cfg.mmcore.pop_next_tagged_image()
#     vedio[:, ...] = np.reshape(tagged_image.pix, [tagged_image.tags["Height"], tagged_image.tags["Width"]])
#     tags[i] = tagged_image.tags

#%%
import time
mm = acq_loop.device_cfg.mmcore
# mm.clear_circular_buffer()

acq_loop.device_cfg.arduino_core.trigger_pattern = 32
acq_loop.device_cfg.arduino_core.start_blanking_mode()

if not mm.is_sequence_running():
    mm.start_continuous_sequence_acquisition(100000)
# mm.prepare_sequence_acquisition(mm.get_camera_device())
# mm.start_continuous_sequence_acquisition(0)
exp = 11.
img_buffer = []
for i in range(100):
    t1 = time.time()
    im_num = mm.get_remaining_image_count()
    t2 = time.time()
    acq_loop.device_cfg.arduino_core.cmd((3, 1, 0, 0))
    while mm.get_remaining_image_count() - im_num == 0:
        pass
    img_buffer.append(mm.pop_next_image())
    exp += 1
    mm.set_exposure(exp)
    t3 = time.time()
    print(t3-t1)
    print(mm.get_remaining_image_count())

mm.stop_sequence_acquisition(mm.get_camera_device())
