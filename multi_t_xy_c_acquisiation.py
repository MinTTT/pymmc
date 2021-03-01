# %%
import pymm as mm
import time
import pymm_device_light_path_cfg as pymm_cfg
import os
from pymm_uitls import colors, get_filenameindex
import _thread as thread

bcolors = colors()
core = mm.core
core.set_property('Core', 'TimeoutMs', 40000)
studio = mm.studio


class PymmAcq:

    def __init__(self, device: str):
        self.device_name = device
        self.stop = [False]

    def multi_acq_3c(self, dir: str, pos_ps: str, time_step: list, flu_step: int, time_duration: list):
        thread.start_new_thread(multi_acq_3c,
                                (dir, pos_ps, self.device_name, time_step, flu_step, time_duration, self.stop))
        return None

    def stop_acq_loop(self):
        self.stop[0] = True
        return None


def get_exposure(state, device_cfg):
    if state == 'green':
        return device_cfg.EXPOSURE_GREEN
    else:
        return device_cfg.EXPOSURE_RED


def if_acq(loop_index, flu_step):
    try:
        reamin = loop_index % flu_step
        return reamin
    except ZeroDivisionError:
        return 1


def multi_acq_3c(dir: str, pos_ps: str, device: str, time_step: list, flu_step: int, time_duration: list,
                 thread_flag=False) -> None:
    '''
    :param dir: image save dir, str
    :param pos_ps: position file, str
    :param device: device tag, str
    :param time_step: list [h, min, s]
    :param flu_step: int
    :param time_duration: list [h, min, s]
    :param thread_flag: list
    :return: None
    '''
    DIR = dir
    POSITION_FILE = pos_ps
    MICROSCOPE = device  # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ
    # -----------------------------------------------------------------------------------

    # %%
    # ==========get multiple positions============
    fovs = mm.parse_position(POSITION_FILE)
    # ==========set loop parameters===============
    time_step = time_step  # [hr, min, s]
    flu_step = flu_step  # very 4 phase loops acq
    time_duration = time_duration
    loops_num = mm.parse_second(time_duration) // mm.parse_second(time_step)
    print(
        f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

    # %% loop body
    device_cfg = pymm_cfg.MicroscopeParas(MICROSCOPE)
    EXPOSURE_PHASE = device_cfg.EXPOSURE_PHASE
    set_light_path = device_cfg.set_light_path
    print(f'{colors.OKGREEN}Initial Device Setup.{colors.ENDC}')
    mm.set_light_path('BF', '100X')
    light_path_state = 'green'
    set_light_path(core, 'init_phase')
    set_light_path(core, 'r2g')
    # TODO：I found the python console initialized and performed this code block first time,
    #  the Ti2E_H has no fluorescent emission light.
    print(f'{colors.OKGREEN}Start ACQ Loop.{colors.ENDC}')
    loop_index = 0  # default is 0
    while loop_index != loops_num:
        t_init = time.time()
        mm.autofocus()
        if if_acq(loop_index, flu_step) == 0:
            for fov_index, fov in enumerate(fovs):
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                mm.move_xyz_pfs(fov, step=5)  # move stage xy.
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                # First Channel
                if light_path_state == 'green':
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    mm.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    print('Snap image (green).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    mm.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
                else:
                    print('Snap image (red).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    mm.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
                # Second Channel
                if light_path_state == 'green':
                    set_light_path(core, 'g2r')
                    light_path_state = 'red'
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    mm.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
                    print(f'Snap image (red).\n')
                else:
                    light_path_state = 'green'
                    set_light_path(core, 'r2g')
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    mm.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    print('Snap image (green).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    mm.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
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
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                print('Snap image (phase).\n')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                mm.auto_acq_save(image_dir, name=file_name,
                                 exposure=EXPOSURE_PHASE)

        # ======================waiting cycle=========
        if thread_flag != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None
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
    return None


if __name__ == '__mian__':
    # ------------------------ acq parameters ----c--------------------------------
    # EXPOSURE_GREEN = 100  # 50 ms TiE2
    # EXPOSURE_PHASE = 20  # ms
    # EXPOSURE_RED = 100  # ms

    DIR = r'G:\20210223'
    POSITION_FILE = r'G:\20210223\multipoints.xml'
    MICROSCOPE = 'Ti2E_LDJ'  # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ
    # -----------------------------------------------------------------------------------

    # %%
    # ==========get multiple positions============
    fovs = mm.parse_position(POSITION_FILE)
    # ==========set loop parameters===============
    time_step = [0, 2, 0]  # [hr, min, s]
    flu_step = 2  # very 4 phase loops acq
    time_duration = [24 * 4, 0, 0]
    loops_num = mm.parse_second(time_duration) // mm.parse_second(time_step)
    print(
        f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

    # %% loop body
    device_cfg = pymm_cfg.MicroscopeParas(MICROSCOPE)
    EXPOSURE_GREEN = device_cfg.EXPOSURE_GREEN
    EXPOSURE_PHASE = device_cfg.EXPOSURE_PHASE
    EXPOSURE_RED = device_cfg.EXPOSURE_RED
    set_light_path = device_cfg.set_light_path
    mm.set_light_path('BF', '100X')
    light_path_state = 'green'
    set_light_path(core, 'init_phase')
    set_light_path(core, 'r2g')
    # TODO：I found the python console initialized and performed this code block first time,
    #  the Ti2E_H has no fluorescent emission light.
    loop_index = 0  # default is 0
    while loop_index != loops_num:
        t_init = time.time()
        if if_acq(loop_index, flu_step) == 0:
            for fov_index, fov in enumerate(fovs):
                mm.move_xyz_pfs(fov, step=5)  # move stage xy.
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                # First Channel
                if light_path_state == 'green':
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    mm.auto_acq_save(image_dir, name=f't{get_filenameindex(image_dir)}',
                                     shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    print('Snap image (green).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    mm.auto_acq_save(image_dir, name=f't{get_filenameindex(image_dir)}',
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
                else:
                    print('Snap image (red).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    mm.auto_acq_save(image_dir, name=f't{get_filenameindex(image_dir)}',
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
                # Second Channel
                if light_path_state == 'green':
                    set_light_path(core, 'g2r')
                    light_path_state = 'red'
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    mm.auto_acq_save(image_dir, name=f't{get_filenameindex(image_dir)}',
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
                    print(f'Snap image (red).\n')
                else:
                    light_path_state = 'green'
                    set_light_path(core, 'r2g')
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    mm.auto_acq_save(image_dir, name=f't{get_filenameindex(image_dir)}',
                                     shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    print('Snap image (green).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    mm.auto_acq_save(image_dir, name=f't{get_filenameindex(image_dir)}',
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
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
                mm.auto_acq_save(image_dir, name=f't{get_filenameindex(image_dir)}',
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
