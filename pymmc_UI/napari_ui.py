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
from typing import Optional
import tifffile as tif
from tqdm import tqdm


# from Acq_test import AcqTrigger

class Rand_camera:

    def __init__(self, imsize=(2048, 2048), depth=np.uint16):
        self._image_size = imsize
        self._depth = depth
        self._flag = None
        self.napari_viewer = None  # type: Optional[napari.Viewer]
        self._img_gen = None
        self.colormap_set = {'green': 'green', 'red': 'red', 'bf': 'gray'}

    def open_viewer(self):
        try:
            if self.napari_viewer is None:
                self.napari_viewer = napari.Viewer()
            self.napari_viewer.show()
        except RuntimeError:
            self.napari_viewer = napari.Viewer()
            self.napari_viewer.show()
        return None

    def start_live(self, obj, channel_name):
        self._flag = True
        if self.napari_viewer is None:
            self.napari_viewer = napari.Viewer()

        self.camera_live(obj, channel_name)

    def stop_live(self):
        self._flag = False

    def update_layer(self, args):
        """
        Parameters:
            args: tuple
                (new_image, layerName)
        """
        new_image, layerName = args
        try:
            # if the layer exists, update the data
            self.napari_viewer.layers[layerName].data = new_image
        except KeyError:
            # otherwise add it to the viewer
            try:
                cmap = self.colormap_set[layerName]
            except KeyError:
                cmap = 'gray'
            self.napari_viewer.add_image(new_image,
                                         name=layerName,
                                         blending='additive',
                                         colormap=cmap)

    def camera_live(self, obj, layer_name):
        @thread_worker(connect={'yielded': self.update_layer})
        def _camera_image(obj, layer_name):
            if self._flag is None:
                self._flag = True
            while obj.live_flag:
                # time.sleep(0.0001)

                while obj.mmCore.get_remaining_image_count() == 0:
                    time.sleep(0.1)
                    pass
                if obj.mmCore.get_remaining_image_count() > 0:
                    # obj.img_buff[im_count] = obj.mmCore.pop_next_image().reshape(obj.img_shape)
                    obj.img_buff = obj.mmCore.get_last_image().reshape(obj.img_shape)
                    # print(im_count)
                    yield obj.img_buff, layer_name
            obj.napari.stop_live()
            obj.trigger.stop_trigger_continuously()
            obj.mmCore.stop_sequence_acquisition()
            obj.stopAcq()
            return None

        if not obj.acq_state:
            obj.initAcq()
        print('start live!')
        obj.trigger.trigger_continuously()
        obj.live_flag = True
        _camera_image(obj, layer_name)
        return None

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
        """

        :param args: (new_imgs, layerindex, layername)
        :return:
        """
        new_imgs, layerindex, layername = args
        try:
            # if the layer exists, update the data
            self.napari_viewer.layers[layername].data = new_imgs
        except KeyError:
            # otherwise add it to the viewer
            self.napari_viewer.add_image(new_imgs, name=layername)
        self.napari_viewer.dims.set_point(0, layerindex)
        return None

    def update_index_from_AcqTrigger(self, obj):
        @thread_worker(connect={'yielded': self.update_layer})
        def _update_index(obj):
            im_count = 0
            obj.current_index = 0
            pbar = tqdm(total=len(obj.img_buff))  # create progress bar
            while im_count < len(obj.img_buff):
                _time_cur = time.time()
                while obj.mmCore.get_remaining_image_count() == 0:
                    pass
                if obj.mmCore.get_remaining_image_count() > 0:
                    obj.img_buff[im_count, ...] = obj.mmCore.pop_next_image().reshape(obj.img_shape)
                    yield obj.img_buff[im_count, ...], obj.current_channel
                    obj.current_index = im_count
                    im_count += 1
                    pbar.update(1)

            obj.trigger.stop_trigger_continuously()
            obj.stopAcq()
            pbar.close()
            yield obj.img_buff, obj.current_channel
            return None

        _update_index(obj)

        return None

    def update_index(self, args):
        """
        update image index
        :param args: (axis, index)
        :return:
        """
        axis, index = args
        self.napari_viewer.dims.set_point(axis, index)
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
if __name__ == '__main__':
    camera = Rand_camera()
    for i in range(3):
        imgs = camera.acq_random_images(20, 0.1, f'random vedio{i}', r'./')

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
