# %%

from pymmc_UI.ND_pad_main_py import NDRecorderUI, FakeAcq
from napari.qt.threading import thread_worker
import napari
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QShortcut
from PyQt5 import QtCore, QtGui, QtWidgets
from magicgui.widgets import FloatRangeSlider, Container, FloatSpinBox, Label
from magicgui import widgets
import Acq_parameters as acq_paras
from pycromanager import Studio
from pycromanager import Core
import json
from pymm_uitls import colors, get_filenameindex, countdown, parse_second, parse_position, NDRecorder, h5_image_saver
import threading as thread
import tifffile as tiff
import pycromanager
import pymm as mm
from device.prior_device import PriorScan
from device.arduino import TriggerArduinoDue
from typing import Optional, Annotated
import time
import numpy as np
from tqdm import tqdm
from threading import Thread
from math import fabs
from re import T
import sys
import os


sys.path.append(r'../')


# from pymmc_UI.napari_ui import Rand_camera
# from device.NI_FPGA import NIFPGADevice


# import imp

# from napari.qt.threading import FunctionWorker, thread_worker
# from napari.types import ImageData, LayerDataTuple
#
# from skimage import data

# from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QShortcut, QWidget
# from PySide2.QtCore import Qt, QObject
# from PySide2.QtGui import QKeySequence
# from pymmc_UI.pymmc_ND_pad import Ui_MainWindow
# from napari.qt.threading import FunctionWorker, thread_worker
# from napari.types import ImageData, LayerDataTuple
#
# from skimage import data
thread_lock = thread.Lock()
core = Core()
studio = Studio()


def threaded(func):
    """
    Decorator that multithreads the target function
    with the given parameters. Returns the thread
    created for the function
    """

    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args)
        thread.start()
        return thread

    return wrapper


def minute2Time(minute: float):
    return '%i:%i:%.1f' % (minute // 60, minute % 60 // 1, minute % 60 % 1 * 60)


class microConfigManag:
    def __init__(self, config_dict=None,
                 UI: Optional[napari.Viewer] = None):
        if config_dict is None:
            config_dict = {}
        self.config_dict = config_dict
        self.UI = UI

    @property
    def config_names(self):
        return list(self.config_dict.keys())

    def get_config(self, name):
        return self.config_dict[name]

    def load_configs(self, config_dict: dict):
        for key, inst in config_dict.items():
            self.config_dict[key] = inst

    def load_config(self, name, config_dict: dict):
        for key, value in config_dict.items():
            self.config_dict[name][key] = value

    def manipulate_AcqControl(self):
        pass

    def manipulate_UI(self):
        pass


def javaList(strVector):
    return [strVector.get(i) for i in range(strVector.size())]


class mmDevice(object):
    """
    This is a wrapper for device that controlled by micromanager.
    """
    device_name = None
    MMCore = None
    property_list = []

    def __init__(self, device_name: str, mmCore: pycromanager.Core):
        self.device_name = device_name
        self.mmCore = mmCore
        self.property_list = self.__getDeviceProperties()
        # self.property_dict = self.__getPropertiesValue()
        self.allowed_property_value = self.__getAllAllowedProVal()
        # self.__add_non_read_only_property(self.property_list)

    def __getDeviceProperties(self):
        return javaList(self.mmCore.get_device_property_names(self.device_name))

    def __getPropertiesValue(self):
        return {pro_name: core.get_property(self.device_name, pro_name) for pro_name in self.property_list}

    def __getAllAllowedProVal(self):
        return {pro_name: javaList(core.get_allowed_property_values(self.device_name, pro_name))
                for pro_name in self.property_list}

    def __setattr__(self, key, value):
        if key in self.property_list:
            self.set_property(key, value)
        else:
            self.__dict__[key] = value

    def __getattr__(self, item):
        if item in self.property_list:
            return self.property_dict[item]
        else:
            return self.__dict__[item]

    @property
    def property_dict(self):
        return self.__getPropertiesValue()

    def get_property(self, propertyName: str):
        # self.property_dict = self.__getPropertiesValue()
        return self.property_dict[propertyName]

    def set_property(self, propertyName, propertyValue):
        allowed_value = self.allowed_property_value[propertyName]
        if allowed_value:
            if propertyValue not in allowed_value:
                raise ValueError(f'Allowed values for device {
                                 self.device_name} are {allowed_value}.')
        self.mmCore.set_property(self.device_name, propertyName, propertyValue)

    def export_device_property(self, export_path=None):
        config = {self.device_name: self.property_dict}
        jsconfig = json.dumps(config)
        if export_path is None:
            export_path = f"./cfg_folder/{self.device_name}_cfg_{
                time.strftime('%Y-%m-%d-%H-%M')}.json"
        with open(export_path, 'w') as cfg_file:
            cfg_file.write(jsconfig)

    def load_device_property(self, path):
        with open(path, 'r') as cfg_file:
            jsconfigs = json.load(cfg_file)

        device_cfg = jsconfigs[self.device_name]
        for keys, pars in device_cfg.items():
            try:
                self.set_property(keys, pars)
            finally:
                pass


class AcqTrigger:
    def __init__(self, mmDeviceName=None, mmCore=None, trigger=None):
        if mmDeviceName is None:
            # this depends on the devices of microscopes
            mmDeviceName = acq_paras.trigger_device
        # type: Optional[mmDevice] # wrapper for controlling camera
        self.camera = None
        # type: Optional[mmDevice] # wrapper for controlling phase light
        self.dia = None
        # type: Optional[mmDevice] # wrapper for controlling LED light
        self.flu = None
        self.filter = None
        self.mmCore = mmCore
        # self.trigger = NIFPGADevice(bitfile=NIbitfile, resource=MIresource)
        if trigger:
            self.trigger = trigger
        else:
            self.trigger = TriggerArduinoDue(com=acq_paras.COM_Arduino)
        self.triggerMap = acq_paras.trigger_map
        self.current_index = 0

        self.channel_dict = acq_paras.channels
        # crate device wrappers
        for key, name in mmDeviceName.items():
            self.__dict__[key] = mmDevice(name, self.mmCore)

        self.acq_state = False
        self.img_shape = None
        self.img_depth = None
        self.buffer_size = 1000
        self._get_img_info()
        self.buffer = np.zeros(
            (self.buffer_size, *self.img_shape), dtype=self.img_depth)

        self.live_flag = False
        self.current_channel = 'Custom'
        print(f'AcqTrigger -> Connect.')
        # self.stopAcq()

    def set_channel(self, channel_name):
        """
        Standard API for setting exposure time, light source intensity.

        Parameters
        ----------
        channel_name: str
            the keys in channel_dict

        Returns
        -------

        """

        channel_set = self.channel_dict[channel_name]  # type: dict
        for key, item in channel_set.items():
            if key == 'exciterSate':
                self.exciterSate = item
            elif key == 'exposure':
                self.exposure = item
            elif key == 'intensity':
                for name, level in item.items():
                    if name == 'Intensity':
                        self.dia.Intensity = level
                    else:
                        self.flu.__setattr__(name, level)
                    mm.waiting_device()
            elif key == 'filter':
                if item:
                    for name, level in item.items():
                        self.filter.set_property(name, level)
                        mm.waiting_device()
            self.current_channel = channel_name
        return None

    def _get_img_info(self):
        depth_dict = {16: np.uint16, 8: np.uint8, 12: np.uint16}
        width, height = self.mmCore.get_image_width(), self.mmCore.get_image_height()
        self.img_shape = (height, width)
        self.img_depth = depth_dict[self.mmCore.get_image_bit_depth()]

    @property
    def exciterSate(self):
        return self.trigger.OutPutPinMap

    @exciterSate.setter
    def exciterSate(self, state: str):
        self.trigger.OutPutPinMap = self.triggerMap[state]

    @property
    def exposure(self):
        """
        Return
        ---------------
        Exposure time in ms
        """
        exposure_time = self.trigger.ONTime / 1000
        # exposure_time = self.camera.get_property('Exposure')  # get camera exposure time
        return float(exposure_time)

    @exposure.setter
    def exposure(self, exposure_time):
        """
        Set exposure time in ms
        """
        self.trigger.ONTime = exposure_time * 1000
        # self.camera.set_property('Exposure', exposure_time)  # set camera exposure time

    def initAcq(self):
        """
        Prepare for image acquisition,
        1. clean circular buffer
        2. start continous sequence acquisition
        """
        if self.mmCore.is_sequence_running():
            self.mmCore.stop_sequence_acquisition()
        else:
            self.mmCore.prepare_sequence_acquisition(self.camera.device_name)

        self.mmCore.clear_circular_buffer()
        self.mmCore.start_continuous_sequence_acquisition(1)
        self._get_img_info()
        self.acq_state = True
        mm.waiting_device()

    def stopAcq(self):
        """
        Stop images acquisition
        1. stop sequence running
        2. clear the circular buffer
        """
        if self.mmCore.is_sequence_running():
            self.mmCore.stop_sequence_acquisition()
        self.mmCore.clear_circular_buffer()
        self.trigger.stop_trigger_continuously()
        self.acq_state = False

    def snap(self, triggermode='TTL') -> tuple:
        """
        Performance: set exposure time, 8 models of light, 879 ms ± 39.6 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
        100 ms on channel

        triggermode: str
            'TTL' or 'MMCore', default is 'software'. This depends on the paramters of camera.

        Returns
        --------------
        image_obj, imgtag: np.ndarray, dict
            (snape image, image info)
        """
        # 1. init acquisition
        self.initAcq()
        # 2. Trigger once
        if triggermode == 'TTL':
            self.trigger.trigger_one_pulse()
        # 2.a if camera trigger mode set to software, use API from MMCore
        elif triggermode == 'MMCore':
            self.mmCore.snap_image()
        while True:
            if self.mmCore.get_remaining_image_count() == 1:
                break
            time.sleep(0.01)
        # 3. get image from MMCore
        jv_img = self.mmCore.pop_next_tagged_image()
        image = jv_img.pix.reshape(self.img_shape)
        imgtag = jv_img.tags
        # # 4. update image in buffer
        # if self.buffer is None:
        #     self.buffer = np.zeros((1000, *self.img_shape), dtype=self.img_depth)

        # self.buffer[self.current_index, ...] = image

        self.stopAcq()
        return image, imgtag

    @thread_worker
    def _continuous_acq(self, duration_time: float, step: float):
        """
        :param duration_time: duration time, how long will acquisition lasting. unit: ms
        :param step: time interval. unit: ms
        """
        print(f'AcqTrigger -> Start Sequential Acq.')
        self._get_img_info()
        one_step_time = self.trigger.ONTime + self.trigger.OFFTime
        # one_step_time = self.exposure
        if one_step_time > step:
            self.trigger.FrameRate = 1000. / step
            # self.exposure = step
        else:
            self.trigger.OFFTime = int(step * 1000 - self.trigger.ONTime)
            # self.exposure = step
        one_step_time = self.trigger.ONTime + self.trigger.OFFTime
        frame_num = int(duration_time * 1e3 / one_step_time)
        # create a buffer
        self.buffer = np.zeros(
            (round(frame_num), *self.img_shape), dtype=self.img_depth)

        if not self.acq_state:
            self.initAcq()
        print('start acq!')
        self.trigger.trigger_continuously()
        im_count = 0
        self.current_index = 0
        pbar = tqdm(total=frame_num)  # create progress bar
        while im_count < frame_num:
            _time_cur = time.time()
            while self.mmCore.get_remaining_image_count() == 0:
                pass
            if self.mmCore.get_remaining_image_count() > 0:
                self.buffer[im_count, ...] = self.mmCore.pop_next_image().reshape(
                    self.img_shape)
                self.current_index = im_count
                im_count += 1
                pbar.update(1)
        self.trigger.stop_trigger_continuously()
        pbar.close()
        self.stopAcq()
        vedio = self.buffer  # clean the buffer
        print(f'FPS: {1e3 / one_step_time: .4f}.')
        return vedio

    def continuous_acq(self,  duration_time: float, step: float):
        worker = self._continuous_acq(duration_time, step)
        worker.start()

    @thread_worker
    def _live(self):
        print('AcqTrigger -> Start live')
        self.live_flag = True
        # 1. init acquisition
        # create a buffer or clean buffer, Since the AcqViewer shall get image
        # buffer before star the live for creating layer. The buffer is not allowed
        # create here for show steaming of the vedio from camera.
        if self.buffer is None:
            frame_num = None
            self.buffer = np.zeros((frame_num, *self.img_shape), dtype=self.img_depth)
            self.buffer_size = len(self.buffer)
        # if not self.acq_state:
        if not self.acq_state:
            self.initAcq()

        self.trigger.trigger_continuously()

        self.current_index = 0

        while self.live_flag:
            # _time_cur = time.time()
            while self.mmCore.get_remaining_image_count() == 0:
                pass
            if self.mmCore.get_remaining_image_count() > 0:
                self.current_index = (
                    self.current_index + 1) % self.buffer_size
                self.buffer[self.current_index, ...] = self.mmCore.pop_next_image().reshape(
                    self.img_shape)

        self.trigger.stop_trigger_continuously()
        self.stopAcq()
        return 0

    def live(self):
        # worker = Thread(target=self._live, args=())
        # worker.start()
        worker = self._live()
        worker.start()

    def live_stop(self):
        self.live_flag = False
    #
    # def show_live(self):
    #     @thread_worker
    #     def _camera_image(obj, layer_name, verbose=False):
    #         print('start live!')
    #         if verbose:
    #             im_count = 0
    #         if self.napari._flag is None:
    #             self.napari._flag = True
    #
    #         while obj.live_flag:
    #             while obj.mmCore.get_remaining_image_count() == 0:
    #                 time.sleep(0.0001)
    #             image = obj.mmCore.get_last_image().reshape(obj.img_shape)
    #             # obj.img_buff = obj.mmCore.pop_next_image().reshape(obj.img_shape)
    #             if verbose:
    #                 im_count += 1
    #                 print(im_count)
    #             yield image, layer_name
    #         print('Stop Live!')
    #         return None
    #
    #     self.napari._flag = True
    #     if self.napari.napari_viewer is None:
    #         self.napari.napari_viewer = napari.Viewer()
    #
    #     if not self.acq_state:
    #         self.initAcq()
    #
    #     self.trigger.trigger_continuously()
    #     self.live_flag = True
    #     # _camera_image(self, 'Live')
    #
    #     worker = _camera_image(self, 'Live', False)
    #     worker.yielded.connect(self.napari.update_layer)
    #     worker.start()
    #     # self.napari.start_live(self, channel_name='Live')
    #     return None
    #
    # def stop_live(self):
    #     self.live_flag = False
    #     self.napari._flag = False
    #     self.stopAcq()
    #     return None


class imgSave:
    def __init__(self, dir=None, name=None, data=None, axes=None, meta=None):
        self.dir = dir
        self.axes = axes
        self.name = name
        self.meta = meta
        self.data = data
        self.suffix = None
        self.main_name = None
        self.index = None
        self.file_name = None
        if self.dir is not None:
            self.get_index()
            self.save()

    def get_index(self):
        if self.name:
            self.suffix = self.name.split('.')[-1]
            self.main_name = self.name.split('.')[0]
            image_list = [file.split('.')[0] for file in os.listdir(
                self.dir) if file.split('.')[-1] == self.suffix]
            image_same_name = [int(file.split('_')[-1]) for file in image_list
                               if len(file.split('_')) >= 2 and file.split('_')[0] == self.main_name]
            if image_same_name:
                self.index = max(image_same_name) + 1
            else:
                self.index = 1

    def save(self, dir=None, name=None, data=None, axes=None, meta=None):
        if dir is not None:
            self.dir = dir
            self.get_index()
        if name is not None:
            self.name = name
            self.get_index()
        if data is not None:
            self.data = data
        if axes is not None:
            self.axes = axes
        if meta is not None:
            self.meta = meta

        self.file_name = os.path.join(self.dir, f'{self.main_name}_{
                                      self.index}.{self.suffix}')
        self.meta['axes'] = self.axes
        # self.meta['']
        # tiff.imwrite(self.file_name, data=self.data,
        #              photometric='minisblack',
        #              metadata=self.meta, ome=True, bigtiff=True)
        with tiff.TiffWriter(self.file_name, bigtiff=True, ome=True) as tif:
            tif.write(self.data, metadata=self.meta)

        self.index += 1
        return None


class AcqControl:
    def __init__(self, mmDeviceName=None, mmCore=None, acq_trigger=None):
        """
        mmDeviceName: dict
            a dictionary records the devices that controlled by micromanager.

        """
        if mmDeviceName is None:
            mmDeviceName = acq_paras.position_device
        self.z = None  # type: Optional[mmDevice]
        self.pfs_state = None  # type: Optional[mmDevice]
        self.pfs_offset = None  # type: Optional[mmDevice]
        # PriorScan(com=4) FakeAcq()
        self.xy = PriorScan(com=acq_paras.COM_PriorScan)

        self.xy_num = None
        self.z_num = None
        self.c_num = None
        self.t_num = None

        self.nd_recorder = NDRecorder()
        # self.napari = Rand_camera(self)
        if acq_trigger is None:
            self.acqTrigger = AcqTrigger(mmCore=mmCore)
        else:
            self.acqTrigger = acq_trigger
        # self.acqTrigger.napari = self.napari  # rewrite Napari of trigger
        self.mmCore = mmCore
        self._current_position = 0
        # crate instance of devices that controlled by micromanager
        for key, name in mmDeviceName.items():
            self.__dict__[key] = mmDevice(name, mmCore)
        print(f'AcqControl -> Initialized.')

    def move_xyz_pfs(self, fov, turnoffz=True, step=6, fov_len=133.3):
        """
        Move stage xy and z position.
        :param fov:
        :param turnoffz: bool, if ture, microscope will keep the pfs working and skipping moving the z device.
        :return: None
        """
        x_f, y_f = self.xy.get_xy_position()
        x_t, y_t = fov['xy'][0], fov['xy'][1]
        dit = np.sqrt((x_t - x_f) ** 2 + (y_f - y_t) ** 2)
        block_size = step * fov_len
        if step == 0:
            num_block = 2
        else:
            num_block = int(dit // block_size + 2)
        x_space = np.linspace(x_f, x_t, num=num_block)
        y_space = np.linspace(y_f, y_t, num=num_block)
        for i in range(len(x_space) - 1):
            self.xy.set_xy_position(x_space[i + 1], y_space[i + 1])
            while self.xy.device_busy():
                time.sleep(0.0001)
        if turnoffz:
            if 'pfsoffset' in fov:
                self.mmCore.set_position(
                    self.pfs_offset.device_name, fov['pfsoffset'][0])
            mm.waiting_autofocus()
        else:
            if 'z' in fov:
                self.mmCore.set_position(self.z.device_name, fov['z'][0])
            mm.waiting_device()
        return None

    def get_position_dict(self, device: Optional[str] = None) -> dict:
        """
        get current position
        :param device: None or string, if device not given, return all devices' positions
        :return: a dict containing positions
        """
        pos = {}
        if device == None:
            device_dict = dict(xy='prior_xy', z=self.z.device_name,
                               pfsoffset=self.pfs_offset.device_name)  # type: dict
            for key, dev in device_dict.items():
                if dev == 'prior_xy':
                    pos[key] = list(self.xy.get_xy_position())
                else:
                    value = self.mmCore.get_position(dev)
                    if isinstance(value, float) or isinstance(value, int):
                        pos[key] = [value]
                    else:
                        pos[key] = value
        return pos

    @property
    def current_position(self) -> Optional[int]:
        return self._current_position

    def record_current_position(self):
        pos = self.get_position_dict()
        self.nd_recorder.add_position(self.get_position_dict())
        self._current_position = self.nd_recorder.position_number - 1
        return pos

    def update_current_position(self):
        current_pos = self.get_position_dict()
        self.nd_recorder.update_position(
            self._current_position, self.get_position_dict())
        return current_pos

    def remove_positions(self, pos_index):
        for i in sorted(pos_index, reverse=True):
            del self.nd_recorder.positions[i]

    def move_right(self, dist=127, convert=False):
        pos = self.get_position_dict()
        if convert:
            pos['xy'][0] -= dist
        else:
            pos['xy'][0] += dist
        self.move_xyz_pfs(pos, step=0)

    def move_left(self, dist=127, convert=False):
        pos = self.get_position_dict()
        if convert:
            pos['xy'][0] += dist
        else:
            pos['xy'][0] -= dist
        self.move_xyz_pfs(pos, step=0)

    def move_up(self, dist=127, convert=False):
        pos = self.get_position_dict()
        if convert:
            pos['xy'][1] -= dist
        else:
            pos['xy'][1] += dist
        self.move_xyz_pfs(pos, step=0)

    def move_down(self, dist=127, convert=False):
        pos = self.get_position_dict()
        if convert:
            pos['xy'][1] += dist
        else:
            pos['xy'][1] -= dist
        self.move_xyz_pfs(pos, step=0)

    def go_to_position(self, index):
        pos = self.nd_recorder.positions[index]
        self.move_xyz_pfs(pos, step=0)
        self._current_position = self.nd_recorder.positions.index(pos)

    def go_to_next_position(self):
        if self._current_position + 1 >= self.nd_recorder.position_number:
            print("Here is the last position.")
            return None
        self._current_position += 1
        self.go_to_position(self._current_position)

    def go_to_previous_position(self):
        if self._current_position <= 0:
            print("Here is the first position.")
            return None
        self._current_position -= 1
        self.go_to_position(self._current_position)


class imageAutoFocus:
    def __init__(self, MSPCtrl: AcqControl,
                 image_score_func=None, z_range=(100, 2000), z_step=20,
                 score_threshold=0,
                 image_mask=None):
        self.ctrl = MSPCtrl
        if image_mask is None:
            self.image_mask = image_mask
        else:
            self.image_mask = None
        if image_score_func is None:
            self.image_score_func = np.var
        else:
            self.image_score_func = image_score_func
        self.score_threshold = score_threshold
        self.z_max = z_range[1]
        self.z_min = z_range[0]
        self.z_step = z_step
        self.z_step_threshold = 0.02
        self.image = None
        self.max_loops = 100

    def get_image(self):
        self.image, _ = self.ctrl.acqTrigger.snap(show=True)
        return self.image

    def eval_score(self):
        self.get_image()
        return self.image_score_func(self.image)

    def move_motor(self, distance):

        self.ctrl.mmCore.set_position(self.ctrl.z.device_name,
                                      self.get_current_z() + distance)
        return None

    def get_current_z(self):
        return self.ctrl.mmCore.get_position(self.ctrl.z.device_name)

    def simaple_AF(self):
        current_score = self.eval_score()
        loop_num = 0
        direction = 1
        step_size = self.z_step
        step_thresh = self.z_step_threshold
        # climb, baby, climb!

        while step_size > step_thresh:
            while loop_num < self.max_loops:
                prev = current_score
                self.move_motor(direction * step_size)
                time.sleep(1)
                curr = self.eval_score()
                print(curr)
                if curr > thresh:
                    print("tres focused")
                    return None

                diff = curr - prev
                curdir = 1 if diff > 0 else -1
                direction = curdir * direction
                if curdir == -1:
                    print("back back back")
                    self.move_motor(direction * step_size)
                    if thresh >= 999999:
                        # naive_autofocus(f, step_size, prev - 100)
                        thresh = prev
                        # return
                    break
                loop_num += 1
            step_size = step_size / 2
        return None


class randCamera:

    def __init__(self, buffer_size: int = 1, y_size: int = 512,
                 x_size: int = 512, time_step: float = 1) -> None:
        self.buffer_size = buffer_size
        self.y_size = y_size
        self.x_size = x_size
        self.time_step = time_step
        self.current_index: int = -1
        self.buffer = np.zeros((buffer_size, y_size, x_size), dtype=np.uint16)
        self.live_flag = False

    def snap(self) -> None:
        self.current_index = (self.current_index + 1) % self.buffer_size
        self.buffer[self.current_index, ...] = np.random.random(
            (self.y_size, self.x_size)) * 2 ** 16
        return None

    @threaded
    def _live(self):
        self.live_flag = True
        while self.live_flag:
            self.current_index = (self.current_index + 1) % self.buffer_size
            self.buffer[self.current_index, ...] = np.random.random(
                (self.y_size, self.x_size)) * 2 ** 16
            time.sleep(self.time_step / 1000)
        return 0

    def live(self):
        # worker = Thread(target=self._live, args=())
        # worker.start()
        worker = self._live()

    def live_stop(self):
        self.live_flag = False


class AcqViewer:

    def __init__(self, acq_trigger: Optional[AcqTrigger] = None,
                 acq_control=None, triggerMap=None, acq_setup=None) -> None:
        self.viewer = napari.Viewer()
        if acq_trigger:
            self.camera = acq_trigger
        else:
            # wrapper for provide images and controlling image acq
            self.camera = randCamera(100, 512, 512)
        if triggerMap:
            self.triggerMap = triggerMap
        else:
            self.triggerMap = acq_paras.trigger_map
        if acq_setup:
            self.acq_setup = acq_setup
        else:
            self.acq_setup = acq_paras.channels
        if acq_control:
            self.acq_control = acq_control
            self.ND_recorder_ui = NDRecorderUI(self.acq_control)
        else:
            self.acq_control = FakeAcq()
            self.ND_recorder_ui = NDRecorderUI(self.acq_control, test=True)
        self.ND_ui = None
        self.acq_config = microConfigManag(
            config_dict=self.acq_setup)  # microConfigManag helps to edit the values in acq_setup
        print(f'[{mm.get_current_time(False)}]AcqViewer -> Creating GUI')
        # GUI 1. live view
        triggerChoiceList = list(self.triggerMap.keys())
        self.acqSetUpChoice = widgets.Combobox(value=self.acq_config.config_names[1],
                                               choices=self.acq_config.config_names,
                                               label='Acquisition Setup')
        exposure_Time = dict(value=20., min=15., max=1000.,
                             step=1.)  # value, min, max, step
        self.intensityBar = widgets.FloatSlider(
            value=0., min=0., max=100., step=1, label='Intensity: ')
        self.startBottom = widgets.ToggleButton(
            text='Start/Stop Live', value=False)
        self.snapBottom = widgets.PushButton(text='Snap', value=False)
        self.acqSetUpAppliedBottom = widgets.PushButton(
            text='Setup apply', value=False)
        self.triggerChoice = widgets.ComboBox(value=triggerChoiceList[0],
                                              choices=triggerChoiceList, label='Trigger type: ')
        self.exposureTime = widgets.FloatSpinBox(
            **exposure_Time, label='Exposure time (ms): ')
        self.configParsWidges = widgets.Container(
            widgets=[self.triggerChoice, self.exposureTime, self.intensityBar])
        self.liveGUI = widgets.Container(widgets=[self.acqSetUpChoice,
                                                  self.configParsWidges,
                                                  self.acqSetUpAppliedBottom,
                                                  widgets.Container(widgets=[self.startBottom, self.snapBottom],
                                                                    layout='horizontal')])

        self.interconnect_change_guipars(
            self.acq_config.config_names[1])  # init all Acq parameters
        self.acqSetUpChoice.changed.connect(self.interconnect_change_guipars)
        self.startBottom.changed.connect(self.connect_triggerBottom)
        self.snapBottom.changed.connect(self.connect_snapBottom)
        self.triggerChoice.changed.connect(
            self.config_connect_change_exciterSate)
        self.exposureTime.changed.connect(self.config_connect_change_exposure)
        self.intensityBar.changed.connect(self.config_connect_change_intensity)
        self.acqSetUpAppliedBottom.changed.connect(self.update_channel_config)
        # GUI x. Sequential Acq
        self.SequentialAcqTime = widgets.FloatSpinBox(value=10,
                                                      min=0,
                                                      label='Lasting time (s): ')
        self.SequentialAcqFrameRate = widgets.FloatSpinBox(value=25,
                                                      min=0,
                                                      label='Frame rate (frames/s): ')
        self.SeqAcqStartBottom = widgets.PushButton(
            text='Start Acq', value=False)
        
        self.SeqAcqGUI = widgets.Container(widgets=[widgets.Container(widgets=[self.SequentialAcqTime,self.SequentialAcqFrameRate], 
                                                    layout='horizontal'),
                                                    self.SeqAcqStartBottom],
                                           layout='vertical')
        self.SeqAcqStartBottom.changed.connect(self.connect_sequencialAcq)
        # GUI 2. ND acq
        self.firstPhase = widgets.Container(
            widgets=[widgets.CheckBox(value=False, text=key)
                                      for key in self.acq_setup.keys()],
            label='1st phase', layout='horizontal')
        self.secondPhase = widgets.Container(
            widgets=[widgets.CheckBox(value=False, text=key)
                                      for key in self.acq_setup.keys()],
            label='2nd phase', layout='horizontal')
        self.firstPhaseNum = widgets.FloatSpinBox(
            value=1, min=1, step=1, label='1st phase number/loop: ')
        self.secondPhaseNum = widgets.FloatSpinBox(
            value=0, min=0, step=1, label='2nd phase number/loop: ')
        self.PhaseNum = widgets.Container(
            widgets=[self.firstPhaseNum, self.secondPhaseNum])
        self.LoopStep = widgets.Container(
            widgets=[widgets.FloatSpinBox(value=1, min=0, step=.1, label='Loop time Step (min): '),
                     widgets.FloatSpinBox(value=1, min=1, step=1, label='Loop number: ')])

        self.estimateTime = widgets.Label(label='Estimate time: ')
        # calcEstimateTime()

        self.LoopStep.changed.connect(self.calcEstimateTime)
        self.PhaseNum.changed.connect(self.calcEstimateTime)
        self.PhaseNum.changed.connect(self.calcEstimateTime)

        # GUI 3. ND pad
        # acq_loop = FakeAcq()
        # NDSelectionUI = NDRecorderUI(acq_loop, test=True)

        # acq_loop.open_NDUI(test_flag=True)
        self.NDSelectionBottom = widgets.PushButton(
            text='Open location selection', value=False)
        self.NDSelectionBottom.changed.connect(self.show_NDSelectionUI)

        # GUI 4. save direct
        self.dirSelect = widgets.FileEdit(
            mode='d', value=os.path.dirname(sys.path[-1]))

        # GUI integration
        self.viewer.window.add_dock_widget(
            self.liveGUI, area='right', name='Acquisition parameter')

        self.viewer.window.add_dock_widget(
            self.SeqAcqGUI, area='right', name='Sequential Acq')

        self.viewer.window.add_dock_widget(widgets.Container(widgets=[self.dirSelect]), area='right',
                                           name='File save directory')
        # pos
        self.viewer.window.add_dock_widget(widgets.Container(widgets=[self.NDSelectionBottom]), area='right',
                                           name='Position selection')
        self.viewer.window.add_dock_widget(widgets.Container(
            widgets=[self.firstPhase, self.secondPhase, self.PhaseNum, self.LoopStep, self.estimateTime]),
            area='right', name='ND setup')
        print(f'[{mm.get_current_time(False)}]AcqViewer -> GUI initialized.')

    def show_NDSelectionUI(self):
        self.viewer.window.add_dock_widget(self.ND_recorder_ui,
                                           area='right')

    def calcEstimateTime(self):
        time = self.LoopStep[0].value * (self.firstPhaseNum.value +
                                         self.secondPhaseNum.value) * self.LoopStep[1].value
        self.estimateTime.value = minute2Time(time)

    def update_point(self, index):
        self.viewer.dims.set_point(axis=0, value=index)

    def update_channel_config(self,):

        channel_name = self.acqSetUpChoice.value
        print(f"AcqViewer -> Update channel: {channel_name} in AcqTrigger.")
        # update the channel setup in acq_trigger
        self.camera.channel_dict[channel_name] = self.acq_setup[channel_name]
        self.camera.set_channel(channel_name)
        print(f"AcqViewer -> Update channel setup Success.")
    # @thread_worker(connect={'yielded': self.update_point})

    @thread_worker
    def get_image_index(self, ):
        index_0 = self.camera.current_index
        time.sleep(1 / 50)
        print(f'AcqViewer -> get_image_index')
        while self.camera.live_flag:
            if self.camera.current_index != index_0:
                index_0 = self.camera.current_index
                time.sleep(1 / 30)  # 30 frame/s is good for all.
                # print(f'AcqViewer -> Image index: {index_0}')

                yield index_0  # delay one frame prventing unnormal display.
        return index_0

    def connect_triggerBottom(self, value):
        print(f'AcqViewer -> triggerBottom = {value}')
        if value:
            # 1. live camera
            self.camera.live()
            # viewer.dims.set_point(axis=0, value=camera.current_index)
            # 2. check live layer
            layer_names = [la.name for la in self.viewer.layers]
            layer_index = 1
            while True:
                layer_name = f'Live_{layer_index}'
                if layer_name not in layer_names:
                    self.viewer.add_image(self.camera.buffer, name=layer_name)
                    break
                else:
                    layer_index += 1
            worker = self.get_image_index()
            worker.yielded.connect(self.update_point)
            worker.start()

            # worker.start()
        else:
            self.camera.live_stop()

    def connect_sequencialAcq(self, value):
        print(f'AcqViewer -> Start Sequential Acq.')
        time_duration = self.SequentialAcqTime.value
        step = 1000 / self.SequentialAcqFrameRate.value
        if time_duration <= 0 or step <= 0:  # check time if validate.
            return 0
        self.camera.continuous_acq(time_duration*1e3, step)
        time.sleep(0.1)  # waiting the image acq start
        # 2. check seq layer
        layer_names = [la.name for la in self.viewer.layers]
        layer_index = 1
        while True:
            layer_name = f'SeqAcq_{layer_index}'
            if layer_name not in layer_names:
                self.viewer.add_image(self.camera.buffer, name=layer_name)
                break
            else:
                layer_index += 1
        worker = self.get_image_index()
        worker.yielded.connect(self.update_point)
        worker.start()
             

    def connect_exposureTime(self, value):
        self.camera.time_step = value

    def connect_triggerChoice(self, value):
        pass

    def connect_snapBottom(self, value):
        print('AcqViewer -> Snap')
        # self.update_channel_config()
        image, imgtag = self.camera.snap()
        channel_name = self.acqSetUpChoice.value
        # ceate layer
        layer_names = [la.name for la in self.viewer.layers]
        index = 1
        while True:
            layername = f'{channel_name}_{index}'
            if layername in layer_names:
                index += 1
            else:
                break
                
        if 'colormap' in list(self.acq_setup[channel_name].keys()):
            colormap = self.acq_setup[channel_name]['colormap'] 
            print(f'AcqViewer -> Create layer {layername}')
            self.viewer.add_image(image, name=layername, colormap=colormap)
        else :
            print(f'AcqViewer -> Create layer {layername}')
            self.viewer.add_image(image, name=layername, rgb=False)
        
        return None

    def interconnect_change_guipars(self, value):
        microconfig = self.acq_config.get_config(value)
        self.exposureTime.value = microconfig['exposure']
        self.triggerChoice.value = microconfig['exciterSate']
        self.intensityBar.value = float(list(microconfig['intensity'].values())[0])
        print(microconfig)

    def config_connect_change_exposure(self, value):
        current_setup = self.acqSetUpChoice.value
        microconfig = self.acq_config.get_config(current_setup)
        microconfig['exposure'] = self.exposureTime.value
        # acq_config.load_config(current_setup, microconfig)

    def config_connect_change_exciterSate(self, value):
        current_setup = self.acqSetUpChoice.value
        microconfig = self.acq_config.get_config(current_setup)
        microconfig['exciterSate'] = self.triggerChoice.value
        # acq_config.load_config(current_setup, microconfig)

    def config_connect_change_intensity(self, value):
        current_setup = self.acqSetUpChoice.value
        microconfig = self.acq_config.get_config(current_setup)
        intensity_key = list(microconfig['intensity'].keys())[0]
        microconfig['intensity'][intensity_key] = self.intensityBar.value
        # acq_config.load_config(current_setup, microconfig)

# class NDRecorder(Container):
    
#     def __init__(self ):
#         super().__init__()
#         self.SetTemp = FloatSpinBox(value=30, min=21, max=45, step=.5)
#         self.append(FloatSpinBox(value=30, min=21, max=45, step=.5))
        
#%%     
        
if __name__ == '__main__':
#%%
    # # scripts for testing AcqViewer 
    # acq_viewer = AcqViewer()
    # napari.run()
    trigger = TriggerArduinoDue('COM13')
    acq_trigger = AcqTrigger(trigger=trigger, mmCore=core)
    acq_trigger.set_channel('bf')

    acq_control = AcqControl(mmDeviceName=acq_paras.position_device, 
                            mmCore=core, acq_trigger=acq_trigger)

    time.sleep(1)
    acq_viewer = AcqViewer(acq_control=acq_control, 
                           acq_trigger=acq_trigger)

# %%
