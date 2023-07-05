# -*- coding: utf-8 -*-

"""

 @author: Pan M. CHU
 @Email: pan_chu@outlook.com
"""

# Built-in/Generic Imports
# […]

# Libs
# […]

# Own modules

from tifffile import TiffWriter
import numpy as np
#%%
data0 = np.random.randint(0, 255, (8, 3, 1024, 1024), 'uint16')

data1 = np.random.randint(0, 1023, (4, 256, 256), 'uint16')


with TiffWriter('temp.ome.tif', ome=True) as tif:
     tif.save(data0, photometric='MINISBLACK',
              metadata={'axes': 'TCYX'}
              )
     tif.save(data1, photometric='MINISBLACK',
     metadata={'axes': 'ZYX', 'SignificantBits': 10,
               'Plane': {'PositionZ': [0.0, 1.0, 2.0, 3.0]}})