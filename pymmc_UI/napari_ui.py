"""
@author: CHU Pan
@email: pan_chu@outlook.com
"""
import time

import napari

from skimage.data import cell, astronaut
import numpy as np
import time
from tqdm import tqdm

random_img = cell()
random_img = random_img * np.random.random(random_img.shape)
np_viewer = napari.Viewer(ndisplay=3)

# napari_viewer = napari.view_image(cell())

#%%
for i in tqdm(range(10)):
    time.sleep(1)
    if np_viewer.layers:
        layer_data = np_viewer.layers[0].data
        layer = np_viewer.layers[0]

        random_img = (np.random.random(random_img.shape) * 2 ** 8 - 1).astype(np.uint8)
        random_imgs = np.concatenate((layer_data, random_img), axis=0)
        layer.data = random_imgs
    else:
        random_img = cell()
        random_img = random_img[np.newaxis, :]
        np_viewer.add_image(random_img, rendering='attenuated_mip')

    np_viewer.dims.set_point(0, layer.data.shape[0]-1)

