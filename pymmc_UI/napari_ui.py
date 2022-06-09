"""
@author: CHU Pan
@email: pan_chu@outlook.com
"""
import time

import napari

import numpy as np
import time
from tqdm import tqdm
from napari.qt.threading import thread_worker

# %%

np_viewer = napari.Viewer()


# napari_viewer = napari.view_image(cell())

def update_layer(new_image):
    try:
        # if the layer exists, update the data
        np_viewer.layers[0].data = new_image
    except IndexError:
        # otherwise add it to the viewer
        np_viewer.add_image(new_image)


@thread_worker(connect={'yielded': update_layer})
def large_random_images(flag=None):
    if flag is None:
        flag = [True]

    random_img = np.random.random((2048, 2048))
    while True:

        time.sleep(.01)
        if flag[0] is True:
            random_img = np.random.random((2048, 2048))

        yield random_img


flag = [True]

large_random_images(flag)  # call the function!
napari.run()
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
