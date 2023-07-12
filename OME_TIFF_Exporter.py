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
import tifffile as tif
from tifffile import TiffWriter, TiffFile
import numpy as np
from lxml import etree
import warnings
from typing import Tuple
import os
from tqdm import tqdm


def getCOMETiffCustomDescription2dict(image_obj: TiffFile):
    desc = getOMETiffMetaDict(image_obj)['Image']['Description']
    return eval(desc)


def getOMETiffMetaDict(image_obj: TiffFile):
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
    node = etree.fromstring(image_obj.ome_metadata.encode('utf-8'), parser=parser)
    desc = elem2dict(node)
    return desc


def getImageData(image_obj: TiffFile) -> Tuple[np.ndarray, dict, str]:
    """
    Read my custom image data.
    Parameters
    ----------
    image_obj : TiffFile
        image instance, read the image use tifffile.TiffFile
    Returns
    -------

    Tuple[np.ndarray, dict, str]
        image data, image custom description, axes
    """
    description = getCOMETiffCustomDescription2dict(image_obj)

    img_series = image_obj.series
    if len(img_series) > 1:
        warnings.warn('length Image Series > 1, only treated first phage.')
    imgs = img_series[0]

    axes = imgs.axes
    imgs_data = imgs.asarray()
    return imgs_data, description, axes


def elem2dict(node, attributes=True):
    """Convert a lxml.etree node tree into a dict.

    Parameters
    ----------
    node :
        Use etree.fromstring() parse a xlsm from string
    attributes : bool
        Ture or False
    Returns
    -------
    dict
        Dictionary result.
    """
    result = {}
    if attributes:
        for item in node.attrib.items():
            key, result[key] = item

    for element in node.iterchildren():
        # Remove namespace prefix
        key = etree.QName(element).localname

        # Process element as tree element if the inner XML contains non-whitespace content
        if element.text and element.text.strip():
            value = element.text
        else:
            value = elem2dict(element)
        if key in result:
            if type(result[key]) is list:
                result[key].append(value)
            else:
                result[key] = [result[key], value]
        else:
            result[key] = value
    return result


# %%
if __name__ == "__main__":
    save_dir = r"D:\zjw\20230704_6_60XRedInit_L3strins_TimeLapse"
    target_dir = r'Z:\Data_Raid\Colony_Project'
    
    def save_ome_tiff(args):
        ome_tif_path, meta, buffer = args
        with TiffWriter(ome_tif_path, ome=True) as ome_tif:
            ome_tif.write(buffer, photometric='MINISBLACK', metadata=meta)
    dir_base_name = os.path.basename(save_dir)
    image_save_dirt = os.path.join(target_dir, dir_base_name)
    fov_dirs = [dir.name for dir in os.scandir(save_dir) if dir.is_dir()]

    # fov_dir = fov_dirs[0]
    for fov_dir in fov_dirs:
        img_list = [img.name for img in os.scandir(os.path.join(save_dir, fov_dirs[0]))
                    if img.name.split('.')[-1] in ['tif', 'tiff']]
        img_list.sort(key=lambda name: int(name.split('.')[0].split('_')[-1]))
        images_data = [tif.TiffFile(os.path.join(save_dir, fov_dir, img_name)) for img_name in tqdm(img_list)]
        # load data from files
        first_image = images_data[0]
        image_data, cust_description, axes = getImageData(first_image)
        image_shape = image_data.shape
        time_data = []
        image_buffer = np.empty((len(images_data), *image_shape), dtype=image_data.dtype)
        for imagei, image in enumerate(tqdm(images_data)):
            image.asarray(out=image_buffer[imagei, ...])
            time_data = time_data + getCOMETiffCustomDescription2dict(image)['Times']
        # Create a new OME TIFF
        save_dir_base_name = os.path.basename(save_dir)
        target_dir_dir = os.path.join(target_dir, save_dir_base_name)
        if not os.path.isdir(target_dir_dir):
            os.mkdir(target_dir_dir)
        with TiffWriter(os.path.join(target_dir_dir, fov_dir + '.ome.tif'), ome=True) as ome_tif:

            description_data = {'Times': time_data}
            for key in list(cust_description.keys()):
                if key != 'Times':
                    description_data[key] = cust_description[key]
            meta_dict = {'axes': 'T' + axes,
                         'Description': description_data}
            ome_tif.save(image_buffer, photometric='MINISBLACK',
                         metadata=meta_dict)
