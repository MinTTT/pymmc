"""
@author: CHU Pan
@email: pan_chu@outlook.com
"""
import os

import napari
# from napari.settings import get_settings
# get_settings().application.ipy_interactive = True
import numpy as np
import time
import threading
from napari.qt.threading import thread_worker

import tifffile as tif


class Rand_camera:

    def __init__(self, imsize=(2048, 2048), depth=np.uint16):
        self._image_size = imsize
        self._depth = depth
        self._flag = None
        self.napari_viewer = None
        self._img_gen = None

    def open_viewer(self):
        try:
            if self.napari_viewer is None:
                self.napari_viewer = napari.Viewer()
            self.napari_viewer.show()
        except RuntimeError:
            self.napari_viewer = napari.Viewer()
            self.napari_viewer.show()
        return None

    def start_live(self):
        self._flag = True
        if self.napari_viewer is None:
            self.napari_viewer = napari.Viewer()

        self.large_random_images()

    def stop_live(self):
        self._flag = False

    def update_layer(self, new_image):
        try:
            # if the layer exists, update the data
            self.napari_viewer.layers['Live camera'].data = new_image
        except KeyError:
            # otherwise add it to the viewer
            self.napari_viewer.add_image(new_image, name='Live camera')

    def large_random_images(self):
        @thread_worker(connect={'yielded': self.update_layer})
        def _large_random_images():
            if self._flag is None:
                self._flag = True

            random_img = (np.random.random(self._image_size) * 2 ** 16).astype(self._depth)
            while self._flag:
                time.sleep(.01)
                random_img = (np.random.random(self._image_size) * 2 ** 16).astype(self._depth)
                yield random_img
            return random_img

        _large_random_images()

    def update_vedio_layers(self, args):
        new_imgs, layerindex, layername = args
        try:
            # if the layer exists, update the data
            self.napari_viewer.layers[layername].data = new_imgs
        except KeyError:
            # otherwise add it to the viewer
            self.napari_viewer.add_image(new_imgs, name=layername)
        self.napari_viewer.dims.set_point(0, layerindex)
        return None

    def acq_random_images(self, duration_time, step, im_name, dir):
        frame_num = round(duration_time / step)
        img_buffer = np.empty(shape=(frame_num, *self._image_size)).astype(self._depth)
        self.open_viewer()

        @thread_worker(connect={'yielded': self.update_vedio_layers})
        def _acq_random_images(buffer, name, dir):
            franme_num = buffer.shape[0]
            for i in range(franme_num):
                time.sleep(step)
                random_img = (np.random.random(self._image_size) * 2 ** 16).astype(self._depth)
                buffer[i, ...] = random_img
                yield buffer, i, im_name
            tif.imsave(os.path.join(dir, f'{name}.tiff'), buffer)
            return None

        _acq_random_images(img_buffer, im_name, dir)
        return None


# %%

camera = Rand_camera()
for i in range(3):
    imgs = camera.acq_random_images(5, 0.1, f'random vedio{i}', r'./')

# flag = [True]
#
# large_random_images(flag)  # call the function!
# np_viewer


# %%

#
# @thread_worker
# def grab_img(np_viewer:napari.Viewer, flag=None, time_step=.01):
#
#     if flag is None:
#         flag = [True]
#     while flag[0]:
#         time.sleep(time_step)
#         if np_viewer.layers:
#             layer_data = np_viewer.layers[0].data
#             layer = np_viewer.layers[0]
#
#             random_img = (np.random.random(random_img.shape) * 2 ** 8 - 1).astype(np.uint8)
#             random_imgs = np.concatenate((layer_data, random_img), axis=0)
#             layer.data = random_imgs
#         else:
#             random_img = cell()
#             random_img = random_img[np.newaxis, :]
#             np_viewer.add_image(random_img, rendering='attenuated_mip')
#
#         np_viewer.dims.set_point(0, layer.data.shape[0] - 1)
#
# flag = [True]
# # threading.Thread(target=grab_img, args=(np_viewer, flag)).start()

# #%%
# for i in tqdm(range(10)):
#     time.sleep(1)
#     if np_viewer.layers:
#         layer_data = np_viewer.layers[0].data
#         layer = np_viewer.layers[0]
#
#         random_img = (np.random.random(random_img.shape) * 2 ** 8 - 1).astype(np.uint8)
#         random_imgs = np.concatenate((layer_data, random_img), axis=0)
#         layer.data = random_imgs
#     else:
#         random_img = cell()
#         random_img = random_img[np.newaxis, :]
#         np_viewer.add_image(random_img, rendering='attenuated_mip')
#
#     np_viewer.dims.set_point(0, layer.data.shape[0]-1)
