# -*- coding: utf-8 -*-

"""
 @auther: Pan M. CHU
"""

import os
import time
import json
from joblib import dump, load
from threading import Lock
import h5py
thread_lock = Lock()


# Own modules
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# %%

class NDRecorder:
    def __init__(self, positions: list = []):
        self._positions = positions  # type: list
        self._pos_num = None

    def __iter__(self):
        self.__currt_i = 0
        self.__iterlen = self._positions.__len__()
        return self

    def __next__(self):
        if self.__currt_i >= self.__iterlen:
            raise StopIteration
        self.__currt_i += 1
        return self._positions[self.__currt_i - 1]

    @property
    def position_number(self):
        self._pos_num = self._positions.__len__()
        return self._pos_num

    @property
    def positions(self):
        return self._positions

    @positions.setter
    def positions(self, pos_list: list):
        self._positions = pos_list

    @property
    def position(self):
        return self._positions[-1]

    @positions.setter
    def positions(self, pos: list):
        self._positions = pos

    @position.setter
    def position(self, pos):
        self.add_position(pos)

    def add_position(self, pos):
        self._positions.append(pos)

    def update_position(self, index, pos):
        self._positions[index] = pos

    def del_position(self, index):
        del self._positions[index]

    def export_pos(self, file_ps):
        try:
            os.makedirs(file_ps)
        except FileExistsError:
            pass
        dump(self.__dict__, os.path.join(file_ps, 'pos.jl'))

    def import_pos(self, file_ps):
        data_dic = load(file_ps)
        self.__dict__.update(data_dic)


# ndr = NDRecorder(list(range(4)))
# for i in ndr:
#     print(i)
# %%

def get_filenameindex(fold_name):
    try:
        file_list = os.listdir(fold_name)
    except FileNotFoundError:
        os.makedirs(fold_name)
        return 0
    tiff_file = [int(name.split('.')[0][1:]) for name in file_list if
                 name.split('.')[-1] == 'tiff' and name.split('.')[0][0] == 't']
    if len(tiff_file) == 0:
        return 0
    return max(tiff_file) + 1


def countdown(t, step=1, trigger=[False], msg='sleeping'):
    """
    a countdown timer print waiting time in second.
    :param trigger: list, a global trigger
    :param t: time lasting for sleeping
    :param step: the time step between the refreshment of screen.
    :param msg:
    :return: None
    """
    CRED = '\033[91m'
    CGRE = '\033[92m'
    CEND = '\033[0m'
    _current_time = time.time()
    while time.time() - _current_time < t:
        mins, secs = divmod(t + _current_time - time.time(), 60)
        thread_lock.acquire()
        print(CRED + f"""{msg} for {int(mins)}:{int(secs)}.""" + CEND, end='\r')
        thread_lock.release()
        time.sleep(step)
        if trigger[0]:
            print(CGRE + 'Stop Acq.' + CEND)
            return None
    # while t > 0:
    #     mins, secs = divmod(t, 60)
    #     print(CRED + f"""{msg} for {int(mins)}:{int(secs)}.""" + CEND, end='\r')
    #     time.sleep(step)
    #     t -= step
    print(CGRE + 'Start the next loop.' + CEND)
    return None


def parse_second(time_list):
    """
    Transform a time list [h, min, s] into seconds.
    :param time_list: list. a list containing [h, min, s]
    :return: float. seconds
    """
    weight = [60 * 60, 60, 1]
    return sum([x * y for x, y in zip(time_list, weight)])


def parse_position(fp, device=None):
    """
    Parse the multiple positions in file. now, this function support files exported
    from micro-manager and Nikon NS.
    :param fp: str, file path
    :return: list, a list containing all positions. each position is a dictionary,
    {xy:[float, float], z:[float], pfsoffset:[float]}
    """
    poss_list = []
    file_type = fp.split('.')[-1]
    if file_type == 'pos':
        with open(fp, 'r') as jfile:
            poss = json.load(jfile)

        poss = poss['map']['StagePositions']['array']
        pos_num = len(poss)

        XY_DEVICE = device[0]  # poss[0]['DefaultXYStage']['scalar']
        Z_DEVICE = device[1]  # poss[0]['DefaultZStage']['scalar']
        PFS_KEY = device[2]  # 'PFSOffset'

        for pos_index in range(pos_num):
            pos = poss[pos_index]['DevicePositions']['array']
            for key in pos:
                if key['Device']['scalar'] == Z_DEVICE:
                    z = key['Position_um']['array']
                if key['Device']['scalar'] == XY_DEVICE:
                    xy = key['Position_um']['array']
                if key['Device']['scalar'] == PFS_KEY:
                    pfs = key['Position_um']['array']
            pos_dic = dict(xy=xy, z=z, pfsoffset=pfs)
            poss_list.append(pos_dic)

    if file_type == 'xml':
        import xml.etree.ElementTree as ET
        poss = ET.parse(fp)
        elemt = poss.getroot()
        for pos in elemt[0]:
            if pos.attrib['runtype'] == 'NDSetupMultipointListItem':
                for e in pos:
                    # print(e.tag, e.attrib)
                    if e.tag == 'dXPosition':
                        xy = [float(e.attrib['value'])]
                    if e.tag == 'dYPosition':
                        xy.append(float(e.attrib['value']))
                    if e.tag == 'dZPosition':
                        z = [float(e.attrib['value'])]
                    if e.tag == 'dPFSOffset':
                        pfs = [float(e.attrib['value'])]
                pos_dic = dict(xy=xy, z=z, pfsoffset=pfs)
                poss_list.append(pos_dic)
    print(f'Get {len(poss_list)} positions.\n')
    return poss_list


def h5_image_saver(image_ps, image_data:dict):
    h5_imag = h5py.File(image_ps, 'w')
    for kws, data in image_data.items():
        h5_imag.create_dataset(kws, data)
    h5_imag.close()
    return None