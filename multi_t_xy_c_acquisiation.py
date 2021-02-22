# %%
import pymm as mm
import time
import pymm_device_light_path_cfg as pymm_cfg
import os
from pymm_uitls import bcolors

core = mm.core
core.set_property('Core', 'TimeoutMs', 40000)
studio = mm.studio


def get_exposure(state):
    if state == 'green':
        return EXPOSURE_GREEN
    else:
        return EXPOSURE_RED


# ------------------------ acq parameters ----c--------------------------------
EXPOSURE_GREEN = 50  # 50 ms TiE2
EXPOSURE_PHASE = 10  # ms
EXPOSURE_RED = 100  # ms

DIR = r'./cfg_folder'
POSITION_FILE = r'G:\Image_Data\moma_data\20210130_pECJ3_M5_L3_2\multipoints.xml'
MICROSCOPE = 'Ti2E'  # Ti2E, Ti2E_H, Ti2E_DB
# -----------------------------------------------------------------------------------
device_cfg = pymm_cfg.Microscope_Paras(MICROSCOPE)
set_light_path = device_cfg.set_light_path
# %%
# ==========get multiple positions============
fovs = mm.parse_position(POSITION_FILE)
# ==========set loop parameters===============
time_step = [0, 3, 30]  # [hr, min, s]
flu_step = 4  # very 4 phase loops acq
time_duration = [48 * 4, 0, 0]
loops_num = mm.parse_second(time_duration) // mm.parse_second(time_step)
print(f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

# %% loop body
mm.set_light_path('BF', '100X')
light_path_state = 'green'
set_light_path(core, 'init_phase')
set_light_path(core, 'r2g')
# TODO：I found the python console initialized and performed this code block first time,
#  the Ti2E_H has no fluorescent emission light.
loop_index = 0  # default is 0
while loop_index != loops_num:
    t_init = time.time()
    if loop_index % flu_step == 0:
        for fov_index, fov in enumerate(fovs):
            mm.move_xyz_pfs(fov, step=5)  # move stage xy.
            print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
            # First Channel
            if light_path_state == 'green':
                print('Snap image (phase).\n')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                mm.auto_acq_save(image_dir, name=f't{loop_index}',
                                 shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                print('Snap image (green).\n')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                mm.auto_acq_save(image_dir, name=f't{loop_index}',
                                 shutter=device_cfg.SHUTTER_LED, exposure=get_exposure(light_path_state))
            else:
                print('Snap image (red).\n')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                mm.auto_acq_save(image_dir, name=f't{loop_index}',
                                 shutter=device_cfg.SHUTTER_LED, exposure=get_exposure(light_path_state))
            # Second Channel
            if light_path_state == 'green':
                set_light_path(core, 'g2r')
                light_path_state = 'red'
                image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                mm.auto_acq_save(image_dir, name=f't{loop_index}',
                                 shutter=device_cfg.SHUTTER_LED, exposure=get_exposure(light_path_state))
                print(f'Snap image (red).\n')
            else:
                light_path_state = 'green'
                set_light_path(core, 'r2g')
                print('Snap image (phase).\n')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                mm.auto_acq_save(image_dir, name=f't{loop_index}',
                                 shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                print('Snap image (green).\n')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                mm.auto_acq_save(image_dir, name=f't{loop_index}',
                                 shutter=device_cfg.SHUTTER_LED, exposure=get_exposure(light_path_state))
    else:
        # ========start phase 100X acq loop=================#
        if light_path_state == 'green':
            pass
        else:
            set_light_path(core, 'r2g')
            light_path_state = 'green'
        mm.active_auto_shutter(device_cfg.SHUTTER_LAMP)
        for fov_index, fov in enumerate(fovs):
            mm.move_xyz_pfs(fov)
            print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
            print('Snap image (phase).\n')
            image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
            mm.auto_acq_save(image_dir, name=f't{loop_index}',
                             exposure=EXPOSURE_PHASE)

    # ======================waiting cycle=========
    t_of_acq = time.time() - t_init
    waiting_t = mm.parse_second(time_step) - t_of_acq
    if waiting_t < 0:
        print(f'{bcolors.WARNING}Waring: Acquisition loop {t_of_acq} s '
              f' is longer than default time step ({-int(waiting_t)} s)! '
              f' and the the next step will start immediately.{bcolors.ENDC}')
    else:
        print(f'Waiting next loop[{loop_index + 1}].')
        mm.countdown(waiting_t, 1)
    loop_index += 1
    # ======================waiting cycle=========

print('finished all loops!')

# # %%
# mm.set_light_path('FLU', 'RFP_100', SHUTTER_LED)
# mm.waiting_device()
# im, tags = mm.snap_image(exposure=EXPOSURE_GREEN)
# mm.save_image(im, dir=DIR, name='test', meta=tags)
