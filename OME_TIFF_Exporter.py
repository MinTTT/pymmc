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

from tifffile import TiffWriter, TiffFile
import numpy as np
from lxml import etree
import warnings
from typing import Tuple


def getCOMETiffCustomDescription2dict(image_obj: TiffFile):
    desc = getOMETiffMetaDict(image_obj)['Image']['Description']
    return eval(desc)


def getOMETiffMetaDict(image_obj: TiffFile):
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
    node = etree.fromstring(image_obj.pages[0].description.encode('utf-8'), parser=parser)
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

    img_series = img.series
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
    data0 = np.random.randint(0, 255, (3, 3, 1024, 1024), 'uint16')
    AcqTime = [1, 3, 4]

    # data1 = np.random.randint(0, 1023, (4, 256, 256), 'uint16')

    with TiffWriter('temp.ome.tif', ome=True) as tif:
        tif.save(data0, photometric='MINISBLACK',
                 metadata={'axes': 'TCYX',
                           'Description': {'Times': AcqTime}},
                 )

    img = TiffFile('temp.ome.tif')

    data, des, axes = getImageData(img)
