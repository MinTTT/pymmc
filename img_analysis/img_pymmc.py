import numpy as np
import matplotlib.pyplot as plt

import tifffile as tiff
import os
from scipy.ndimage import histogram
import sys
# import matplotlib

# matplotlib.use('TkAgg')

# %%
img_ps = r'C:\Users\pan_c\Desktop'
img_names = [file for file in os.listdir(img_ps) if file.split('.')[-1] == 'tiff']
img = tiff.imread(os.path.join(img_ps, img_names[0]))

# img_hist = histogram(img, 0, np.median(img)*1.5, 5000)

fig1, ax = plt.subplots(1, 1)
density_range = (img.min(), np.median(img)*1.5)
ax.hist(img.flatten(), bins=int(np.ptp(density_range)), range=density_range)

fig1.show()
