# %%
import pymm as mm

core = mm.core
core.set_property('Core', 'TimeoutMs', 40000)


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
            core.set_property(FILTER_TURRET, 'State', 3)
            mm.waiting_device()
        if shift_type == 'g2r':
            core.set_property(SHUTTER_LED, 'Green_Level', RED_EXCITE)
            core.set_property(SHUTTER_LED, 'Green_Enable', 1)
            core.set_property(SHUTTER_LED, 'Cyan_Enable', 0)
            core.set_property(FILTER_TURRET, 'State', 7)
            mm.waiting_device()
    return None


def get_exposure(state):
    if state == 'green/':
        return EXPOSURE_GREEN
    else:
        return EXPOSURE_RED


# ------------------------ acq parameters ----c--------------------------------
EXPOSURE_GREEN = 50  # ms
EXPOSURE_PHASE = 40  # ms
EXPOSURE_RED = 100  # ms

DIR = r'D:/DATA/FULAB/ZJW/test/'
POSITION_FILE = r'./cfg_folder/PositionList.pos'
MICROSCOPE = 'Ti2E_H'

# --------------------------Initial Microscope Parameters-----------------------
if MICROSCOPE == 'Ti2E':
    SHUTTER_LAMP = 'DiaLamp'
    SHUTTER_LED = 'XCite-Exacte'
    FILTER_TURRET = 'FilterTurret1'
    FLU_EXCITE = 'XCite-Exacte'
    GREEN_EXCITE = 5
    RED_EXCITE = 50
    XY_DEVRED_EXCITEICE = core.get_xy_stage_device()
elif MICROSCOPE == 'Ti2E_H':
    SHUTTER_LAMP = 'DiaLamp'
    SHUTTER_LED = 'Spectra'
    FILTER_TURRET = 'LudlWheel'
    GREEN_EXCITE = 50
    RED_EXCITE = 50
# -----------------------------------------------------------------------------------

# %%
# ==========get multiple positions============
fovs = mm.parse_position(POSITION_FILE)
# ==========set loop parameters===============
time_step = [0, 0, 5]  # [hr, min, s]
flu_step = 2  # very 4 phase loops acq
time_duration = [48, 0, 0]
loops_num = mm.parse_second(time_duration) // mm.parse_second(time_step)
print(f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

# %% loop body
mm.set_light_path('BF', '100X', SHUTTER_LAMP)
light_path_state = 'green/'
loop_index = 0  # default is 0
while loop_index != loops_num:
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
                im, tags = mm.snap_image(exposure=get_exposure(light_path_state))
                print('Snap image (red).\n')
                image_dir = DIR + f'fov_{fov_index}/' + light_path_state
                mm.save_image(im, dir=image_dir, name=f't{loop_index}', meta=tags)
            # Second Channel
            if light_path_state == 'green/':
                # mm.set_light_path('FLU', 'RFP_100', SHUTTER_LED)
                green_to_red(core, 'g2r', micro_device=MICROSCOPE)
                light_path_state = 'red/'
                im, tags = mm.snap_image(exposure=get_exposure(light_path_state))
                print(f'Snap image (red).\n')
                image_dir = DIR + f'fov_{fov_index}/' + light_path_state
                mm.save_image(im, dir=image_dir, name=f't{loop_index}', meta=tags)
            else:
                light_path_state = 'green/'
                # mm.set_light_path('BF', '100X', SHUTTER_LAMP)
                green_to_red(core, 'r2g', micro_device=MICROSCOPE)
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
    print(f'Waiting next loop[{loop_index + 1}].')
    mm.countdown(mm.parse_second(time_step), 1)
    loop_index += 1

# # %%
# mm.set_light_path('FLU', 'RFP_100', SHUTTER_LED)
# mm.waiting_device()
# im, tags = mm.snap_image(exposure=EXPOSURE_GREEN)
# mm.save_image(im, dir=DIR, name='test', meta=tags)
