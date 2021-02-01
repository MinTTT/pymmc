# %%
import json
import os
import time

import numpy as np
# from pycromanager import Acquisition, multi_d_acquisition_events
import tifffile as tiff
from pycromanager import Bridge

bridge = Bridge()
global core
core = bridge.get_core()

studio = bridge.get_studio()


def get_current_time():
    """
    get current time.
    :return: formatted time: Year-Month-Day-Hours-Minutes-Seconds,Seconds
    """
    formatted_time = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()) + ',' + str(time.time())
    return formatted_time


def snap_image(**kwargs):
    """
    get current image in fov
    :param kwargs: 'exposure'
    :return:
    """
    # core = bridge.get_core()
    if 'exposure' in kwargs:
        core.set_exposure(kwargs['exposure'])
    core.snap_image()
    tagged_image = core.get_tagged_image()  # re
    im = np.reshape(tagged_image.pix,
                    newshape=[tagged_image.tags["Height"], tagged_image.tags["Width"]])
    return im, tagged_image.tags


def save_image(im, im_dir, name, meta):
    """
    save image acquired to defined dir.
    :param im: ndarray
    :param meta: dictionary, some tags
    :param im_dir: str, save folder
    :param name: str, image name
    :return: NULL
    """
    try:
        os.makedirs(im_dir)
    except FileExistsError:
        pass
    save_im_dir = im_dir + name + '.tiff'
    meta['time'] = get_current_time()
    tiff.imwrite(file=save_im_dir, data=im, metadata=meta)
    return None


def auto_acq_save(im_dir, name, exposure: float, shutter=None):
    if shutter:
        active_auto_shutter(shutter)
    im, meta = snap_image(exposure=exposure)
    # TODO: threading.
    save_image(im, im_dir, name, meta)
    return None


def active_auto_shutter(shutter):
    """
    Set the active shutter when switch the light path.
    :param shutter: str, shutter name.
    :return: None.
    """
    core.set_shutter_device(shutter)
    core.set_auto_shutter(True)
    return None


def set_light_path(grop, preset, shutter=None):
    """
    set the light path of microscope
    :param grop: str, group of mm configuration
    :param preset: str, preset of mm configuration
    :param shutter: str, set the shutter given at auto state
    :return: None
    """
    core.set_config(grop, preset)
    # wait device finish
    if shutter:
        active_auto_shutter(shutter)
    waiting_device()
    return None


def parse_position(fp):
    """
    Parse the multiple positions in file. now, this function support files exported
    from micro-manager and Nikon NS.
    :param fp: str, file path
    :return: list, a list containing all positions. each position is a dictionary,
    {xy:[float, float], z:[float], pfsoffset:[float]}
    """
    poss_list = []
    file_type = fp.split('.')[-1]
    if file_type == 'pos':
        with open(fp, 'r') as jfile:
            poss = json.load(jfile)
        poss = poss['map']['StagePositions']['array']
        pos_num = len(poss)
        XY_DEVICE = poss[0]['DefaultXYStage']['scalar']
        Z_DEVICE = poss[0]['DefaultZStage']['scalar']
        PFS_KEY = 'PFSOffset'

        for pos_index in range(pos_num):
            pos = poss[pos_index]['DevicePositions']['array']
            for key in pos:
                if key['Device']['scalar'] == Z_DEVICE:
                    z = key['Position_um']['array']
                if key['Device']['scalar'] == XY_DEVICE:
                    xy = key['Position_um']['array']
                if key['Device']['scalar'] == PFS_KEY:
                    pfs = key['Position_um']['array']
            pos_dic = dict(xy=xy, z=z, pfsoffset=pfs)

            poss_list.append(pos_dic)

    if file_type == 'xml':
        import xml.etree.ElementTree as ET
        poss = ET.parse(fp)
        elemt = poss.getroot()
        for pos in elemt[0]:
            if pos.attrib['runtype'] == 'NDSetupMultipointListItem':
                for e in pos:
                    # print(e.tag, e.attrib)
                    if e.tag == 'dXPosition':
                        xy = [float(e.attrib['value'])]
                    if e.tag == 'dYPosition':
                        xy.append(float(e.attrib['value']))
                    if e.tag == 'dZPosition':
                        z = [float(e.attrib['value'])]
                    if e.tag == 'dPFSOffset':
                        pfs = [float(e.attrib['value'])]
                pos_dic = dict(xy=xy, z=z, pfsoffset=pfs)
                poss_list.append(pos_dic)
    print(f'Get {len(poss_list)} positions.\n')
    return poss_list


def waiting_device():
    """
    waiting for micro-scope done all commands.
    :return: None
    """
    while core.system_busy():
        time.sleep(0.0001)
    return None


def parse_second(time_list):
    """
    Transform a time list [h, min, s] into seconds.
    :param time_list: list. a list containing [h, min, s]
    :return: float. seconds
    """
    weight = [60 * 60, 60, 1]
    return sum([x * y for x, y in zip(time_list, weight)])


def move_xyz_pfs(fov, turnoffz=True, step=3, fov_len=133.1):
    """
    Move stage xy and z position.
    :param fov:
    :param turnoffz: bool, if ture, microscope will keep the pfs working and skipping moving the z device.
    :return: None
    """
    XY_DEVICE = core.get_xy_stage_device()
    if 'xy' in fov:
        x_f, y_f = core.get_x_position(XY_DEVICE), core.get_y_position(XY_DEVICE)
        x_t, y_t = fov['xy'][0], fov['xy'][1]
        dit = np.sqrt((x_t - x_f) ** 2 + (y_f - y_t) ** 2)
        block_size = step * fov_len
        num_block = int(dit // block_size + 2)
        x_space = np.linspace(x_f, x_t, num=num_block)
        y_space = np.linspace(y_f, y_t, num=num_block)
        for i in range(len(x_space) - 1):
            core.set_xy_position(XY_DEVICE, x_space[i + 1], y_space[i + 1])
            waiting_device()

    if turnoffz:
        if 'pfsoffset' in fov:
            core.set_auto_focus_offset(fov['pfsoffset'][0])
    else:
        if 'z' in fov:
            core.set_position(fov['z'][0])
    # waiting_device()
    return None


def countdown(t, step=1, msg='sleeping'):
    """
    a countdown timer print waiting time in second.
    :param t: time lasting for sleeping
    :param step: the time step between the refreshment of screen.
    :param msg:
    :return: None
    """
    CRED = '\033[91m'
    CGRE = '\033[92m'
    CEND = '\033[0m'
    while t > 0:
        mins, secs = divmod(t, 60)
        print(CRED + f"""{msg} for {int(mins)}:{int(secs)}.""" + CEND, end='\r')
        time.sleep(step)
        t -= step
    print(CGRE + 'Start the next loop.' + CEND)
    return None


# # %%
# EXPOSURE_GREEN = 50  # ms
# EXPOSURE_PHASE = 10  # ms
# EXPOSURE_RED = 100  # ms
#
# DIR = r'./test_data/test1/'
# POSITION_FILE = r'./test_data/PositionList.pos'
# SHUTTER_LAMP = 'DiaLamp'
# SHUTTER_LED = 'XCite-Exacte'
# SHUTTER_TURRET = 'Turret1Shutter'
# XY_DEVICE = core.get_xy_stage_device()
# fovs = parse_position(POSITION_FILE)
# # %%
# count = 0
# time_step = [0, 10, 0]  # [hr, min, s]
# time_duration = [4, 0, 0]
# loops = parse_second(time_duration) // parse_second(time_step)
# set_light_path('BF', '40X', SHUTTER_LAMP)
# while loops:
#     for fov_index, fov in enumerate(fovs):
#         move_xyz_pfs(fov)
#         # acquire photos
#         im, tags = snap_image()
#         waiting_device()
#         image_dir = DIR + f'fov_{fov_index}/'
#         save_image(im, dir=image_dir, name=f'lp{loops}_test{count}', meta=tags)
#
#         print(f'go to next xy')
#         count += 1
#     print('Waiting next loop')
#     countdown(parse_second(time_step), 10)
#     loops -= 1
#
#
#
# # %%
# set_light_path('BF', '100X', SHUTTER_LAMP)
# waiting_device()
# im, tags = snap_image()
# save_image(im, dir=DIR, name='test', meta=tags)
# %%
if __name__ == '__main__':
    countdown(10)
