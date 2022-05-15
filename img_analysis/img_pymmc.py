import numpy as np
import matplotlib.pyplot as plt

import tifffile as tiff
import os
from scipy.ndimage import histogram
import sys
import matplotlib

# matplotlib.use('TkAgg')

# %%
img_ps = r'C:\Users\pc\Desktop\streads\HDR_random_exp'
img_names = os.listdir(img_ps)

# img_hist = histogram(img, 0, 2**8, 1000)


fig1, ax = plt.subplots(1, 1)

img_range = (2000, 12200)
# bin_num = np.ptp(img_range)

for i in range(5):
    img = tiff.imread(os.path.join(img_ps, img_names[i]))
    ax.hist(img.flatten(), bins=1000, range=img_range, label=f'image{i}')

img_control = tiff.imread(r'F:\zjw\20211010_NH2_pECJ3_M5_updownshift\fov_11\phase\t0.tiff')
ax.hist(img_control.flatten(), bins=1000, range=img_range, label=f'HamamatsuHam_DCAM')
ax.set_xlabel('Intensity')
ax.set_ylabel('Density')
ax.legend()
fig1.show()




medium_imgs = [np.median(tiff.imread(os.path.join(img_ps, img_name))) for img_name in img_names]


fig2, ax = plt.subplots(1, 1)

img_range = (0, 3000)
# bin_num = np.ptp(img_range)


img = tiff.imread(os.path.join(img_ps, img_names[63]))
ax.hist(img.flatten(), bins=3000, range=img_range, label=f'image{63}')

img_control = tiff.imread(r'F:\zjw\20211010_NH2_pECJ3_M5_updownshift\fov_11\phase\t0.tiff')
ax.hist(img_control.flatten(), bins=3000, range=img_range, label=f'HamamatsuHam_DCAM')
ax.set_xlabel('Intensity')
ax.set_ylabel('Density')
ax.legend()
fig2.show()