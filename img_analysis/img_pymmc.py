import numpy as np
import matplotlib.pyplot as plt

import tifffile as tiff
import os
from scipy.ndimage import histogram




img_ps = r'C:\Users\pc\Desktop\streads\HDR_random_exp\test0.tiff'

img = tiff.imread(img_ps)