# %%
import pymm as mm

core = mm.core
core.set_property('Core', 'TimeoutMs', 40000)

EXPOSURE_GREEN = 50  # ms
EXPOSURE_PHASE = 10  # ms
EXPOSURE_RED = 100  # ms

DIR = r'G:/Image_Data/moma_data/20201221_NH2_PECJ3/'
POSITION_FILE = r'G:/Image_Data/moma_data/20201221_NH2_PECJ3/multipoints.xml'
SHUTTER_LAMP = 'DiaLamp'
SHUTTER_LED = 'XCite-Exacte'
SHUTTER_TURRET = 'Turret1Shutter'
XY_DEVICE = core.get_xy_stage_device()


def get_exposure(state):
    if state == 'green/':
        return EXPOSURE_GREEN
    else:
        return EXPOSURE_RED


# %%
# ==========get multiple positions============
fovs = mm.parse_position(POSITION_FILE, file_type='ns')
# ==========set loop parameters===============
time_step = [0, 3, 0]  # [hr, min, s]
flu_step = 4  # very 4 phase loops acq
time_duration = [48, 0, 0]
loops_num = mm.parse_second(time_duration) // mm.parse_second(time_step)
print(f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

# %% loop body
loop_index = 5  # default is 0
while loop_index != loops_num:
    if loop_index % flu_step == 0:
        light_path_state = 'green/'
        for fov_index, fov in enumerate(fovs):
            mm.move_xyz_pfs(fov)  # move stage xy.
            print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
            # First Channel
            if light_path_state == 'green/':

                mm.set_light_path('BF', '100X', SHUTTER_LAMP)
                im, tags = mm.snap_image()
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

                mm.set_light_path('FLU', 'RFP_100', SHUTTER_LED)
                light_path_state = 'red/'
                im, tags = mm.snap_image(exposure=get_exposure(light_path_state))
                print(f'Snap image (red).\n')
                image_dir = DIR + f'fov_{fov_index}/' + light_path_state
                mm.save_image(im, dir=image_dir, name=f't{loop_index}', meta=tags)
            else:
                light_path_state = 'green/'
                mm.set_light_path('BF', '100X', SHUTTER_LAMP)
                im, tags = mm.snap_image()
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
        mm.set_light_path('BF', '100X', SHUTTER_LAMP)
        for fov_index, fov in enumerate(fovs):
            mm.move_xyz_pfs(fov)
            print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
            mm.waiting_device()
            # acquire photos
            im, tags = mm.snap_image()
            print('Snap image (phase).\n')
            image_dir = DIR + f'fov_{fov_index}/' + 'phase/'
            mm.save_image(im, dir=image_dir, name=f't{loop_index}', meta=tags)

    # ======================waiting cycle=========
    print(f'Waiting next loop[{loop_index+1}].')
    mm.countdown(mm.parse_second(time_step), 1)
    loop_index += 1

# # %%
# mm.set_light_path('FLU', 'RFP_100', SHUTTER_LED)
# mm.waiting_device()
# im, tags = mm.snap_image(exposure=EXPOSURE_GREEN)
# mm.save_image(im, dir=DIR, name='test', meta=tags)
