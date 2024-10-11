# -*- coding: utf-8 -*-

"""

 @author: Pan M. CHU
 @Email: pan_chu@outlook.com
"""

# Built-in/Generic Imports
import os
import sys
# […]

# Libs
import pandas as pd
import numpy as np  # Or any other
# […]
from shutil import copyfile
# Own modules
import tifffile as tiff
from tqdm import tqdm

def Acq_ROI_apply(data: np.ndarray, index_ax1: int, index_ax2: int,
                  ax1_length: int, ax2_length: int) -> np.ndarray:
    data_roi = data[index_ax1:index_ax1 + ax1_length, index_ax2:index_ax2 + ax2_length]
    return data_roi


axis0 = 662
axis1 = 0
axis0_len = 700
axis1_length = 2048


source_directory = r'D:\Fulab\zjw\20240813_RDM-Gluc_Toggle-L3'
target_directory = r'Z:\chupan\Data_Raid\Colony_Project\Moma_data\20240813_RDM-Gluc_Toggle-L3'


fov_dir = os.listdir(source_directory)

for fov in tqdm(fov_dir):
    fov_path = os.path.join(source_directory, fov)
    target_fov = os.path.join(target_directory, fov)
    if os.path.isfile(fov_path):
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        copyfile(fov_path, target_fov)
    else:
        if not os.path.exists(target_fov):
            os.makedirs(target_fov)
        # get channel dirs
        channel_dirs = [channel for channel in os.listdir(fov_path)
                        if os.path.isdir(os.path.join(fov_path, channel))]
        for channel in channel_dirs:
            channel_path = os.path.join(fov_path, channel)
            target_channel_path = os.path.join(target_fov, channel)
            if not os.path.isdir(target_channel_path):
                os.makedirs(target_channel_path)
            image_list = [image for image in os.listdir(channel_path) if image.split('.')[-1] == 'tiff']
            for image in image_list:
                if not os.path.exists(os.path.join(target_channel_path, image)):

                    image_path = os.path.join(channel_path, image)
                    target_image_path = os.path.join(target_channel_path, image)
                    with tiff.TiffFile(image_path) as image_data:
                            image_array = image_data.asarray()
                            image_meta = image_data.imagej_metadata
                            if image_meta is None:
                                image_meta = image_data.shaped_metadata[0]
                                image_meta = {key: image_meta[key] for key in ['acq_time', 'axes'] if key in image_meta.keys()}
                    data_roi = Acq_ROI_apply(image_array, axis0, axis1, axis0_len, axis1_length)
                    with tiff.TiffWriter(target_image_path, imagej=True) as file_roi:
                        file_roi.save(data_roi, metadata=image_meta)

