# -*- coding: utf-8 -*-

"""

 @author: Pan M. CHU
 @Email: pan_chu@outlook.com
"""

# Built-in/Generic Imports
from calendar import c
from concurrent.futures import thread
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
from threading import Thread

def Acq_ROI_apply(data: np.ndarray, index_ax1: int, index_ax2: int,
                  ax1_length: int, ax2_length: int) -> np.ndarray:
    image_size = data.shape
    ax1_end = index_ax1 + ax1_length if index_ax1 + ax1_length < image_size[0] else image_size[0]
    ax2_end = index_ax2 + ax2_length if index_ax2 + ax2_length < image_size[1] else image_size[1]
    data_roi = data[index_ax1:ax1_end, index_ax2:ax2_end]
    return data_roi

def convert_image_date_type(data: np.ndarray, target_dtype: np.dtype, clip=False) -> np.ndarray:
    """
    Convert the data type of the image data.
    
    """
    target_date_type_max = np.iinfo(target_dtype).max
    if clip:
        data = np.clip(data, 0, target_date_type_max)  # Clip data to avoid overflow
    else: # rescale data
        data = (data / np.max(data) * target_date_type_max).astype(target_dtype)
    data = np.asarray(data, dtype=target_dtype)
    return data.astype(target_dtype)

def _thread_image_list_save(image_list, channel_path, target_channel_path, axis0, axis1, axis0_len, axis1_length, channel_config):
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
                if channel in channel_config:
                    try:
                        data_type = channel_config[channel]['data_type']
                        data_roi = convert_image_date_type(data_roi, data_type)
                    except KeyError:
                        pass
                file_roi.save(data_roi, metadata=image_meta)

axis0 = 0
axis1 = 0
axis0_len = 2048 - axis0
axis1_length = 2048
time_range = (0, 920)

source_directory = r'D:\Fulab\zjw\20250819_Moma_NH5.17-CPP713-pSC101-PfliC_MOPS-Gluc'
target_directory = r'Z:\chupan\Data_Raid\xcd001_proj\microscopy_data\20250819_Moma_NH5.17-CPP713-pSC101-PfliC_MOPS-Gluc'


channel_config = {'bf': {'data_type': np.uint8}}

fov_dir = os.listdir(source_directory)
threads_list = []
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
            image_list = [image for image in os.listdir(channel_path) if image.split('.')[-1] in 'tiff']
            # sort image by last number in nale
            image_list.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
            # filter images by time range
            image_list = [image for image in image_list if time_range[0] <= int(image.split('_')[-1].split('.')[0]) <= time_range[1]]
            worker = Thread(target=_thread_image_list_save, args=(image_list, channel_path, 
                                                                         target_channel_path, axis0, axis1, axis0_len, axis1_length, channel_config))
            worker.start()
            threads_list.append(worker)
        for thread in threads_list:
            thread.join()
            # for image in image_list:
            #     if not os.path.exists(os.path.join(target_channel_path, image)):
            #         image_path = os.path.join(channel_path, image)
            #         target_image_path = os.path.join(target_channel_path, image)
            #         with tiff.TiffFile(image_path) as image_data:
            #                 image_array = image_data.asarray()
            #                 image_meta = image_data.imagej_metadata
            #                 if image_meta is None:
            #                     image_meta = image_data.shaped_metadata[0]
            #                     image_meta = {key: image_meta[key] for key in ['acq_time', 'axes'] if key in image_meta.keys()}
            #         data_roi = Acq_ROI_apply(image_array, axis0, axis1, axis0_len, axis1_length)
            #         with tiff.TiffWriter(target_image_path, imagej=True) as file_roi:
            #             if channel in channel_config:
            #                 try:
            #                     data_type = channel_config[channel]['data_type']
            #                     data_roi = convert_image_date_type(data_roi, data_type)
            #                 except KeyError:
            #                     pass
            #             file_roi.save(data_roi, metadata=image_meta)

