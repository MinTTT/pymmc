# %%

import time
import pymm_device_light_path_cfg as pymm_cfg
import os
from pymm_uitls import colors, get_filenameindex, countdown, parse_second, parse_position
import _thread as thread

bcolors = colors()

# studio = mm.studio


class PymmAcq:

    def __init__(self, device: str):
        self.device_name = device
        self.stop = [False]

    def multi_acq_3c(self, dir: str, pos_ps: str, time_step: list, flu_step: int, time_duration: list):
        thread.start_new_thread(multi_acq_3c,
                                (dir, pos_ps, self.device_name, time_step, flu_step, time_duration, self.stop))
        return None

    def multi_acq_4c(self, dir: str, pos_ps: str, time_step: list, flu_step: int, time_duration: list):
        thread.start_new_thread(multi_acq_4c,
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
    device_cfg = pymm_cfg.MicroscopeParas(MICROSCOPE)
    # %%
    # ==========get multiple positions============
    fovs = parse_position(POSITION_FILE,
                             device=[device_cfg.XY_DEVICE, device_cfg.Z_DEVICE, device_cfg.AUTOFOCUS_OFFSET])
    # ==========set loop parameters===============
    time_step = time_step  # [hr, min, s]
    flu_step = flu_step  # very 4 phase loops acq
    time_duration = time_duration
    loops_num = parse_second(time_duration) // parse_second(time_step)
    print(
        f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

    # %% loop body

    EXPOSURE_PHASE = device_cfg.EXPOSURE_PHASE
    set_device_state = device_cfg.set_device_state
    print(f'{colors.OKGREEN}Initial Device Setup.{colors.ENDC}')
    device_cfg.set_light_path('BF', '100X')
    light_path_state = 'green'
    set_device_state(device_cfg.mmcore, 'init_phase')
    set_device_state(device_cfg.mmcore, 'r2g')
    # TODO：I found the python console initialized and performed this code block first time,
    #  the Ti2E_H has no fluorescent emission light.
    print(f'{colors.OKGREEN}Start ACQ Loop.{colors.ENDC}')
    loop_index = 0  # default is 0
    while loop_index != loops_num:
        t_init = time.time()
        if if_acq(loop_index, flu_step) == 0:
            for fov_index, fov in enumerate(fovs):
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                device_cfg.move_xyz_pfs(fov, step=6, XY_DEVICE=device_cfg.XY_DEVICE)  # move stage xy.
                device_cfg.autofocus()  # check auto focus, is important!
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                # First Channel
                if light_path_state == 'green':
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    print('Snap image (green).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
                else:
                    print('Snap image (red).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
                # Second Channel
                if light_path_state == 'green':
                    set_device_state(device_cfg.mmcore, 'g2r')
                    light_path_state = 'red'
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
                    print(f'Snap image (red).\n')
                else:
                    light_path_state = 'green'
                    set_device_state(device_cfg.mmcore, 'r2g')
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    print('Snap image (green).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                     shutter=device_cfg.SHUTTER_LED,
                                     exposure=get_exposure(light_path_state, device_cfg))
        else:
            # ========start phase 100X acq loop=================#
            if light_path_state == 'green':
                pass
            else:
                set_device_state(device_cfg.mmcore, 'r2g')
                light_path_state = 'green'
            device_cfg.active_auto_shutter(device_cfg.SHUTTER_LAMP)
            for fov_index, fov in enumerate(fovs):
                device_cfg.move_xyz_pfs(fov, step=6, XY_DEVICE=device_cfg.XY_DEVICE)
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                print('Snap image (phase).\n')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                device_cfg.auto_acq_save(image_dir, name=file_name,
                                 exposure=EXPOSURE_PHASE)

        # ======================waiting cycle=========

        t_of_acq = time.time() - t_init
        waiting_t = parse_second(time_step) - t_of_acq

        if thread_flag != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None

        if waiting_t < 0:
            print(f'{bcolors.WARNING}Waring: Acquisition loop {t_of_acq} s '
                  f' is longer than default time step ({-int(waiting_t)} s)! '
                  f' and the the next step will start immediately.{bcolors.ENDC}')
        else:
            print(f'Waiting next loop[{loop_index + 1}].')
            countdown(waiting_t, 1)
        if thread_flag != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None
        loop_index += 1
        # ======================waiting cycle=========

    print('finished all loops!')
    return None



def multi_acq_4c(dir: str, pos_ps: str, device: str, time_step: list, flu_step: int, time_duration: list,
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
    device_cfg = pymm_cfg.MicroscopeParas(MICROSCOPE)
    # %%
    # ==========get multiple positions============
    fovs = parse_position(POSITION_FILE,
                             device=[device_cfg.XY_DEVICE, device_cfg.Z_DEVICE, device_cfg.AUTOFOCUS_OFFSET])
    # ==========set loop parameters===============
    time_step = time_step  # [hr, min, s]
    flu_step = flu_step  # very 4 phase loops acq
    time_duration = time_duration
    loops_num = parse_second(time_duration) // parse_second(time_step)
    print(
        f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

    # %% loop body

    EXPOSURE_PHASE = device_cfg.EXPOSURE_PHASE
    set_device_state = device_cfg.set_device_state
    print(f'{colors.OKGREEN}Initial Device Setup.{colors.ENDC}')
    device_cfg.set_light_path('BF', '100X', shutter=device_cfg.SHUTTER_LAMP)
    light_path_state = 'green'
    print(f'{colors.OKGREEN}Initial Phase Setup.{colors.ENDC}')
    set_device_state(device_cfg.mmcore, 'init_phase')
    print(f'{colors.OKGREEN}Initial First Channel.{colors.ENDC}')
    set_device_state(device_cfg.mmcore, '3t1')
    # TODO：I found the python console initialized and performed this code block first time,
    #  the Ti2E_H has no fluorescent emission light.
    print(f'{colors.OKGREEN}Start ACQ Loop.{colors.ENDC}')
    loop_index = 0  # default is 0
    while loop_index != loops_num:
        t_init = time.time()
        if if_acq(loop_index, flu_step) == 0:
            for fov_index, fov in enumerate(fovs):
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                device_cfg.move_xyz_pfs(fov, step=6, XY_DEVICE=device_cfg.XY_DEVICE)  # move stage xy.
                device_cfg.autofocus()  # check auto focus, is important!
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                # First Channel
                if light_path_state == 'green':
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    print('Snap image (CFP).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'CFP')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_BLUE)
                    set_device_state(device_cfg.mmcore, '1t2')
                    print('Snap image (YFP).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'YFP')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_YELLOW)
                    set_device_state(device_cfg.mmcore, '2t3')
                    print('Snap image (RED).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'RED')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_RED)
                    light_path_state = 'red'
                else:
                    print('Snap image (RED).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'RED')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_RED)
                    set_device_state(device_cfg.mmcore, '3t2')
                    print('Snap image (YFP).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'YFP')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_YELLOW)
                    set_device_state(device_cfg.mmcore, '2t1')
                    print('Snap image (CFP).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'CFP')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_BLUE)
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    light_path_state = 'green'


        else:
            # ========start phase 100X acq loop=================#
            if light_path_state == 'green':
                pass
            else:
                set_device_state(device_cfg.mmcore, '3t1')
                light_path_state = 'green'
            device_cfg.active_auto_shutter(device_cfg.SHUTTER_LAMP)
            for fov_index, fov in enumerate(fovs):
                device_cfg.move_xyz_pfs(fov, step=6, XY_DEVICE=device_cfg.XY_DEVICE)
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                print('Snap image (phase).\n')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                device_cfg.auto_acq_save(image_dir, name=file_name,
                                 exposure=EXPOSURE_PHASE)

        # ======================waiting cycle=========

        t_of_acq = time.time() - t_init
        waiting_t = parse_second(time_step) - t_of_acq

        if thread_flag != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None

        if waiting_t < 0:
            print(f'{bcolors.WARNING}Waring: Acquisition loop {t_of_acq} s '
                  f' is longer than default time step ({-int(waiting_t)} s)! '
                  f' and the the next step will start immediately.{bcolors.ENDC}')
        else:
            print(f'Waiting next loop[{loop_index + 1}].')
            countdown(waiting_t, 1)
        if thread_flag != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None
        loop_index += 1
        # ======================waiting cycle=========

    print('finished all loops!')
    return None