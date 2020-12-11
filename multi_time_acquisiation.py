#%%
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
#%% get multiple positions
fovs = mm.parse_position(POSITION_FILE, type='ns')
# %% set loop parameters
count = 0
time_step = [0, 2, 30]  # [hr, min, s]
flu_step = 7  # very 4 phase loops acuq
time_duration = [24, 0, 0]
loops_num = mm.parse_second(time_duration) // mm.parse_second(time_step)

#%% loop body
loop_index = 0
while loop_index != loops_num:
    # start phase 100 acq loop
    for fov_index, fov in enumerate(fovs):
        mm.set_light_path('BF', '100X', SHUTTER_LAMP)
        mm.move_xyz_pfs(fov)
        # acquire photos
        im, tags = mm.snap_image()
        mm.waiting_device()
        image_dir = DIR + f'fov_{fov_index}/' + 'phase/'
        mm.save_image(im, dir=image_dir, name=f't{loop_index}', meta=tags)
        print(f'''go to next xy {fov['xy']}.''')
        count += 1
    if loop_index % flu_step == 0:
        for fov_index, fov in enumerate(fovs):
            mm.move_xyz_pfs(fov)
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
#%%
import xml.etree.ElementTree as ET
import xml.dom.minidom
ps = './test_data/multipoints.xml'
poss = ET.parse(ps)
elemt = poss.getroot()
for child in elemt:
    print(child.tag, child.attrib)
pos = elemt[0][2]
poss = []
for pos in elemt[0]:
    if pos.attrib['runtype'] == 'NDSetupMultipointListItem':
        for e in pos:
            print(e.tag, e.attrib)
            if e.tag == 'dXPosition':
                xy = [float(e.attrib['value'])]
            if e.tag == 'dYPosition':
                xy.append(float(e.attrib['value']))
            if e.tag == 'dZPosition':
                z = float(e.attrib['value'])
            if e.tag == 'dPFSOffset':
                pfs = float(e.attrib['value'])
        pos_dic = dict(xy=xy, z=z, pfsoffset=pfs)
        poss.append(pos_dic)

#%%
mm.parse_position(ps, type='ns')
