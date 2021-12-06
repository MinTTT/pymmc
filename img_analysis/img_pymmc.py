import numpy as np
import matplotlib.pyplot as plt

import tifffile as tiff
import os
from scipy.ndimage import histogram
import sys
import matplotlib
# matplotlib.use('TkAgg')

#%%
img_ps = r'C:\Users\pc\Desktop\streads\HDR_random_exp'
img_names = os.listdir(img_ps)
img = tiff.imread(os.path.join(img_ps, img_names[0]))

img_hist = histogram(img, 0, 2**8, 1000)



fig1, ax = plt.subplots(1, 1)

ax.hist(img, bins=1000, range=(0, 2**8))

plt.show()