# %%
import pymm as mm

core = mm.core
# %%
EXPOSURE_GREEN = 50  # ms
EXPOSURE_PHASE = 10  # ms
EXPOSURE_RED = 400  # ms

DIR = r'./test_data/20201211/'
POSITION_FILE = r'./test_data/multipoints.xml'
SHUTTER_LAMP = 'DiaLamp'
SHUTTER_LED = 'XCite-Exacte'
SHUTTER_TURRET = 'Turret1Shutter'
XY_DEVICE = core.get_xy_stage_device()
# %%
# ==========get multiple positions============
fovs = mm.parse_position(POSITION_FILE, type='ns')
# ==========set loop parameters===============
time_step = [0, 2, 30]  # [hr, min, s]
flu_step = 7  # very 4 phase loops acuq
time_duration = [24, 0, 0]
loops_num = mm.parse_second(time_duration) // mm.parse_second(time_step)
print(f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

# %% loop body
loop_index = 5  # default is 0
while loop_index != loops_num:
    # ========start phase 100X acq loop=================#
    mm.set_light_path('BF', '100X', SHUTTER_LAMP)  # set phase contrast light path config before start xy acquisition.
    for fov_index, fov in enumerate(fovs):
        mm.move_xyz_pfs(fov)
        # acquire photos
        im, tags = mm.snap_image()
        mm.waiting_device()
        image_dir = DIR + f'fov_{fov_index}/' + 'phase/'
        mm.save_image(im, dir=image_dir, name=f't{loop_index}', meta=tags)
        print(f'''go to next xy {fov['xy']}.''')
    # ===============================================#
    if loop_index % flu_step == 0:
        for fov_index, fov in enumerate(fovs):
            mm.move_xyz_pfs(fov)  # move stage xy.
            print(f'''go to next xy {fov['xy']}.''')
            # GFP
            mm.set_light_path('FLU', 'GFP_100', SHUTTER_LED)
            mm.waiting_device()
            im, tags = mm.snap_image(exposure=EXPOSURE_GREEN)
            image_dir = DIR + f'fov_{fov_index}/' + 'green/'
            mm.save_image(im, dir=image_dir, name=f't{loop_index}', meta=tags)
            # RFP
            mm.set_light_path('FLU', 'RFP_100', SHUTTER_LED)
            mm.waiting_device()
            im, tags = mm.snap_image(exposure=EXPOSURE_RED)
            image_dir = DIR + f'fov_{fov_index}/' + 'red/'
            mm.save_image(im, dir=image_dir, name=f't{loop_index}', meta=tags)
    print('Waiting next loop')
    mm.countdown(mm.parse_second(time_step), 10)
    loop_index += 1

# # %%
# mm.set_light_path('FLU', 'RFP_100', SHUTTER_LED)
# mm.waiting_device()
# im, tags = mm.snap_image(exposure=EXPOSURE_GREEN)
# mm.save_image(im, dir=DIR, name='test', meta=tags)



