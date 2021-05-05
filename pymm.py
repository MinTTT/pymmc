# %%

import os
import time

import numpy as np
# from pycromanager import Acquisition, multi_d_acquisition_events
import tifffile as tiff
import _thread as thread

from pycromanager import Bridge

bridge = Bridge()
global core
core = bridge.get_core()

studio = bridge.get_studio()


# %%
def get_current_time():
    """
    get current time.
    :return: formatted time: Year-Month-Day-Hours-Minutes-Seconds,Seconds
    """
    formatted_time = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()) + ',' + str(time.time())
    return formatted_time


def mm_set_camer_roi(roi: list, camera: int = 0) -> None:
    """

    :param roi: list, [x, y, Xsize, Ysize]; x	coordinate of the top left corner; y	coordinate of the top left corner; xSize	number of horizontal pixels; ySize	number of horizontal pixels;
    :param camera: int 0 , if set to 0, use current camera
    :return: None
    """
    if camera == 0:
        core.set_roi(*roi)
    return None


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
    save_im_dir = os.path.join(im_dir, f'{name}.tiff')
    meta['time'] = get_current_time()
    tiff.imwrite(file=save_im_dir, data=im, metadata=meta)
    return None


def auto_acq_save(im_dir: str, name: str, exposure: float, shutter=None) -> None:
    """
    auto acquisition image and save.

    :param im_dir: str, path
    :param name: str, image name
    :param exposure: float, set exposure time
    :param shutter: None or str, if None, microscope use current shutter
    :return: None
    """
    if shutter is not None:
        active_auto_shutter(shutter)
    im, meta = snap_image(exposure=exposure)
    thread.start_new_thread(save_image, (im, im_dir, name, meta))
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


def waiting_device(device=None):
    """
    waiting for micro-scope done all commands.
    device:str, device name, if None, waiting all device
    :return: None
    """
    if device is not None:
        while core.device_busy(device):
            time.sleep(0.00001)
        return None
    else:
        while core.system_busy():
            time.sleep(0.00001)
    return None


def waiting_autofocus():
    while not core.is_continuous_focus_locked():
        time.sleep(0.00001)
    return None



def move_xyz_pfs(fov, turnoffz=True, step=6, fov_len=133.3, XY_DEVICE=False):
    """
    Move stage xy and z position.
    :param fov:
    :param turnoffz: bool, if ture, microscope will keep the pfs working and skipping moving the z device.
    :return: None
    """
    if XY_DEVICE is False:
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
        # core.wait_for_device(XY_DEVICE)
            while core.device_busy(XY_DEVICE):
                time.sleep(0.00001)
            # waiting_device()

    if turnoffz:
        if 'pfsoffset' in fov:
            core.set_auto_focus_offset(fov['pfsoffset'][0])
            waiting_autofocus()
    else:
        if 'z' in fov:
            core.set_position(fov['z'][0])
        waiting_device()
    return None


def autofocus():
    if not core.is_continuous_focus_locked():
        core.enable_continuous_focus(True)
        waiting_device()
        print('Auto Focus Enable!')
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
    pass