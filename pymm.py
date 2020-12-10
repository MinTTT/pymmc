# %%
from pycromanager import Bridge
import numpy as np
from pycromanager import Acquisition, multi_d_acquisition_events
import time
import tifffile as tiff
import os
import json
import sys
bridge = Bridge()

bridge.get_core()

core = bridge.get_core()  # if


# studio = bridge.get_studio()


def get_aframe(image, metadata):
    global im
    im.append(image)
    print('acquired!')


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


def save_image(im, dir, name, meta):
    """
    save image acquired to defined dir.
    :param im: ndarray
    :param meta: dictionary, some tags
    :param dir: str, save folder
    :param name: str, image name
    :return: NULL
    """
    try:
        os.makedirs(dir)
    except FileExistsError:
        pass
    save_dir = dir + name + '.tiff'
    meta['time'] = get_current_time()
    tiff.imwrite(file=save_dir, data=im, metadata=meta)
    return None


def active_auto_shutter(shutter):
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
    while core.system_busy():
        time.sleep(0.1)
    if shutter:
        active_auto_shutter(shutter)
    return None


def parse_position(fp, type='mm'):
    """
    Parse the multiple positions in file, now, this function support files exported
    from micro-manager.
    :param fp: str, file path
    :param type: str, file type
    :return: list, a list contat
    """
    if type == 'mm':
        with open(fp, 'r') as jfile:
            poss = json.load(jfile)
        poss = poss['map']['StagePositions']['array']
        pos_num = len(poss)
        XY_DEVICE = poss[0]['DefaultXYStage']['scalar']
        Z_DEVICE = poss[0]['DefaultZStage']['scalar']
        PFS_KEY = 'PFSOffset'
        poss_list = []
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
        print(f'Get {len(poss_list)} positions.\n')
    return poss_list


def waiting_device():
    while core.system_busy():
        time.sleep(0.1)


def parse_second(list):
    weight = [60*60, 60, 1]
    return sum([x*y for x, y in zip(list, weight)])


def move_xyz_pfs(fov, turnoffz=True):
    XY_DEVICE = core.get_xy_stage_device()
    if 'xy' in fov:
        core.set_xy_position(XY_DEVICE, fov['xy'][0], fov['xy'][1])
    if turnoffz:
        if 'pfsoffset' in fov:
            core.set_auto_focus_offset(fov['pfsoffset'][0])
    else:
        if 'z' in fov:
            core.set_position(fov['z'][0])
    waiting_device()
    return None


def countdown(t, step=1, msg='sleeping'):  # in seconds
    pad_str = ' ' * len('%d' % step)
    for i in range(t, 0, -step):
        print('%s for the next %d seconds %s\r' % (msg, i, pad_str))
        sys.stdout.flush()
        time.sleep(step)
    print('Done %s for %d seconds!  %s' % (msg, t, pad_str))

get_current_time()

# %%
EXPOSURE_GREEN = 50  # ms
EXPOSURE_PHASE = 10  # ms
EXPOSURE_RED = 100  # ms

DIR = r'./test_data/test1/'
POSITION_FILE = r'./test_data/PositionList.pos'
SHUTTER_LAMP = 'DiaLamp'
SHUTTER_LED = 'XCite-Exacte'
SHUTTER_TURRET = 'Turret1Shutter'
XY_DEVICE = core.get_xy_stage_device()
fovs = parse_position(POSITION_FILE)
# %%
count = 0
time_step = [0, 10, 0]  # [hr, min, s]
time_duration = [4, 0, 0]
loops = parse_second(time_duration) // parse_second(time_step)
set_light_path('BF', '40X', SHUTTER_LAMP)
while loops:
    for fov_index, fov in enumerate(fovs):
        move_xyz_pfs(fov)
        # acquire photos
        im, tags = snap_image()
        waiting_device()
        image_dir = DIR + f'fov_{fov_index}/'
        save_image(im, dir=image_dir, name=f'lp{loops}_test{count}', meta=tags)

        print(f'go to next xy')
        count += 1
    print('Waiting next loop')
    countdown(parse_second(time_step), 10)
    loops -= 1



# %%
set_light_path('BF', '40X', SHUTTER_LAMP)

im, tags = snap_image()
save_image(im, dir=DIR, name='test', meta=tags)
# %%
if __name__ == '__main__':
    #     with Acquisition(directory=r'.', name='test', show_display=False) as acq:
    #         z_post = core.get_position()
    #         half_range = 0.8  # miu m
    #         events = multi_d_acquisition_events(z_start=z_post - half_range, z_end=z_post + half_range,
    #                                             z_step=0.1)
    #         acq.acquire(events)

    # ACQUISITION　PARAMETERS

    im = []
    with Acquisition(image_process_fn=get_aframe, show_display=False) as acq:
        z_post = core.get_position()
        frams_num = 17
        half_range = 0.8
        step = half_range / (frams_num // 2)
        events = multi_d_acquisition_events(z_start=z_post - half_range, z_end=z_post + half_range,
                                            z_step=step)
        acq.acquire(events)

    images = np.array(im)
    print(f'image size: {images.shape}')
    image1 = np.sum(images[..., 0:8], axis=2)
    image2 = np.sum(images[..., 10:-1], axis=2)
    corr_im = image2 - image1
    corred_im = corr_im - corr_im.min * (255 / (corr_im.max - corr_im.min))
    print(corred_im)
