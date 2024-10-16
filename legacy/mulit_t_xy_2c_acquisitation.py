# %%
import pymm as mm
import time

core = mm.core
core.set_property('Core', 'TimeoutMs', 40000)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def green_to_red(core, shift_type, micro_device='Ti2E'):
    """
    This function is used to set light from green to red channel.
    For Ti2E, two devices shall be changed their states. 1. FilterTurret, filter states
    :param core: mmcore
    :param shift_type: str, 'g2r' or 'r2g'
    :param micro_device: str, which device? 'Ti2E' or 'Ti2E_H'.
    :return: None
    """
    if micro_device == 'Ti2E':
        if shift_type == "g2r":
            core.set_property(FILTER_TURRET, 'State', 5)  # set filer in 5 pos
            core.set_property(FLU_EXCITE, 'Lamp-Intensity', RED_EXCITE)  # set xcite lamp intensity 50
            mm.waiting_device()
        if shift_type == "r2g":
            core.set_property(FILTER_TURRET, 'State', 2)  # set filer in 2 pos
            core.set_property(FLU_EXCITE, 'Lamp-Intensity', GREEN_EXCITE)  # set xcite lamp intensity 2
            mm.waiting_device()
    elif micro_device == 'Ti2E_H':
        if shift_type == "r2g":
            core.set_property(SHUTTER_LED, 'Cyan_Level', GREEN_EXCITE)
            core.set_property(SHUTTER_LED, 'Cyan_Enable', 1)
            core.set_property(SHUTTER_LED, 'Green_Enable', 0)
            # core.set_property(SHUTTER_LED, 'State', 1)
            core.set_property(FILTER_TURRET, 'State', 3)  # pos 3 521
            mm.waiting_device()
        if shift_type == 'g2r':
            core.set_property(SHUTTER_LED, 'Green_Level', RED_EXCITE)
            core.set_property(SHUTTER_LED, 'Green_Enable', 1)
            core.set_property(SHUTTER_LED, 'Cyan_Enable', 0)
            # core.set_property(SHUTTER_LED, 'State', 1)
            core.set_property(FILTER_TURRET, 'State', 5)  # pos5 631/36
            mm.waiting_device()
    return None


def get_exposure(state):
    if state == 'green/':
        return EXPOSURE_GREEN
    else:
        return EXPOSURE_RED


# ------------------------ acq parameters ----c--------------------------------
EXPOSURE_GREEN = 50  # 50 ms TiE2, 100 ms sfGFP
EXPOSURE_PHASE = 10  # ms
EXPOSURE_RED = 100  # ms

DIR = r'G:\Image_Data\moma_data\20210130_pECJ3_M5_L3_2/'
POSITION_FILE = r'G:\Image_Data\moma_data\20210130_pECJ3_M5_L3_2\multipoints.xml'
MICROSCOPE = 'Ti2E'
# --------------------------Initial Microscope Parameters-----------------------
if MICROSCOPE == 'Ti2E':
    SHUTTER_LAMP = 'DiaLamp'
    SHUTTER_LED = 'XCite-Exacte'
    FILTER_TURRET = 'FilterTurret1'
    FLU_EXCITE = 'XCite-Exacte'
    GREEN_EXCITE = 25
    RED_EXCITE = 50
    XY_DEVRED_EXCITEICE = core.get_xy_stage_device()
elif MICROSCOPE == 'Ti2E_H':
    SHUTTER_LAMP = 'DiaLamp'
    SHUTTER_LED = 'Spectra'
    FILTER_TURRET = 'LudlWheel'
    GREEN_EXCITE = 15
    RED_EXCITE = 50
# -----------------------------------------------------------------------------------
# %%
# ==========get multiple positions============
fovs = mm.parse_position(POSITION_FILE)
# ==========set loop parameters===============
time_step = [0, 3, 0]  # [hr, min, s]
flu_step = 4  # very 4 phase loops acq
time_duration = [48 * 4, 0, 0]
loops_num = mm.parse_second(time_duration) // mm.parse_second(time_step)
print(f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

# %% loop body
mm.set_light_path('BF', '100X')
light_path_state = 'green/'
green_to_red(core, 'r2g', MICROSCOPE)
# TODO：I found the python console initialized and performed this code block first time,
#  the Ti2E_H has no fluorescent emission light.
loop_index = 0  # default is 0
while loop_index != loops_num:
    t_init = time.time()
    if loop_index % flu_step == 0:
        for fov_index, fov in enumerate(fovs):
            mm.move_xyz_pfs(fov)  # move stage xy.
            print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
            # First Channel
            if light_path_state == 'green/':
                mm.active_auto_shutter(SHUTTER_LAMP)
                im, tags = mm.snap_image(exposure=EXPOSURE_PHASE)
                print('Snap image (phase).\n')
                image_dir = DIR + f'fov_{fov_index}/' + 'phase/'
                mm.save_image(im, dir=image_dir, name=f't{loop_index}', meta=tags)
                # mm.set_light_path('FLU', 'GFP_100', SHUTTER_LED)
                mm.active_auto_shutter(SHUTTER_LED)
                im, tags = mm.snap_image(exposure=get_exposure(light_path_state))
                print('Snap image (green).\n')
                image_dir = DIR + f'fov_{fov_index}/' + light_path_state
                mm.save_image(im, dir=image_dir, name=f't{loop_index}', meta=tags)

    else:
        # ========start phase 100X acq loop=================#
        if light_path_state == 'green':
            pass
        else:
            green_to_red(core, 'r2g', micro_device=MICROSCOPE)
            light_path_state = 'green/'
        mm.active_auto_shutter(SHUTTER_LAMP)
        for fov_index, fov in enumerate(fovs):
            mm.move_xyz_pfs(fov)
            print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
            mm.waiting_device()
            # acquire photos
            im, tags = mm.snap_image(exposure=EXPOSURE_PHASE)
            print('Snap image (phase).\n')
            image_dir = DIR + f'fov_{fov_index}/' + 'phase/'
            mm.save_image(im, dir=image_dir, name=f't{loop_index}', meta=tags)

    # ======================waiting cycle=========
    t_of_acq = time.time() - t_init
    waiting_t = mm.parse_second(time_step) - t_of_acq
    if waiting_t < 0:
        print(f'{bcolors.WARNING}Waring: Acquisition loop {t_of_acq} s \n is longer than default time step!,'
              f' and the the next step will start immediately.{bcolors.ENDC}')
    else:
        print(f'Waiting next loop[{loop_index + 1}].')
        mm.countdown(waiting_t, 1)
    loop_index += 1

print('finished all loops!')
