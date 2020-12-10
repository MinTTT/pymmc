# %%
from pycromanager import Bridge
import numpy as np
from pycromanager import Acquisition, multi_d_acquisition_events
import time
import tifffile as tiff
import os
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
    core = bridge.get_core()
    if 'exposure' in kwargs:
        core.set_exposure(kwargs['exposure'])
    core.snap_image()
    tagged_image = core.get_tagged_image()  # re
    im = np.reshape(tagged_image.pix,
                    newshape=[tagged_image.tags["Height"], tagged_image.tags["Width"]])
    return im, tagged_image.tags


def save_image(im, meta, dir, name):
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
    tiff.imsave(file=save_dir,
                data=im,
                meta=meta)
    return None


get_current_time()
core.snap_image()
im = core.get_tagged_image()
# %%


if __name__ == '__main__':
    #     with Acquisition(directory=r'.', name='test', show_display=False) as acq:
    #         z_post = core.get_position()
    #         half_range = 0.8  # miu m
    #         events = multi_d_acquisition_events(z_start=z_post - half_range, z_end=z_post + half_range,
    #                                             z_step=0.1)
    #         acq.acquire(events)

    # ACQUISITION　PARAMETERS
    EXPOSURE_GREEN = 50  # ms
    EXPOSURE_PHASE = 10  # ms
    EXPOSURE_RED = 100  # ms

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
