
#%%
import os
import sys
import time

import napari
from napari.qt import thread_worker
import numpy as np
import pymm as mm
import pycromanager
import tifffile as tiff
import threading as thread
from pymm_uitls import colors, get_filenameindex, countdown, parse_second, parse_position, NDRecorder, h5_image_saver
import h5py
from pymmc_UI.napari_ui import Rand_camera, FakeAcq
from device.prior_device import PriorScan
from pycromanager import Core
from pycromanager import Studio
from device.NI_FPGA import NIFPGADevice
from typing import Optional, Callable
import json
from PySide2 import QtWidgets

thread_lock = thread.Lock()

global core
core = Core()

studio = Studio()

from tqdm import tqdm


def javaList(strVector):
    return [strVector.get(i) for i in range(strVector.size())]


class mmDevice(object):
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
                raise ValueError(f'Allowed values for device {self.device_name} are {allowed_value}.')
        self.mmCore.set_property(self.device_name, propertyName, propertyValue)

    def export_device_property(self, export_path=None):
        config = {self.device_name: self.property_dict}
        jsconfig = json.dumps(config)
        if export_path is None:
            export_path = f"./cfg_folder/{self.device_name}_cfg_{time.strftime('%Y-%m-%d-%H-%M')}.json"
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
    def __init__(self, mmDeviceName=None, napri_inst=None,
                 NIbitfile=r'device/NI_FPGA/myRIO_v6.lvbitx', MIresource='rio://172.22.11.2/RIO0',
                 mmCore=None):
        if mmDeviceName is None:
            mmDeviceName = {'camera': 'TUCam', 'flu': 'Spectra', 'dia': 'TIDiaLamp'}
        self.camera = None
        self.dia = None
        self.flu = None
        self.mmCore = mmCore
        self.trigger = NIFPGADevice(bitfile=NIbitfile, resource=MIresource)
        self.triggerMap = {'phase': 0b01000000,
                           'none': 0b00000000,
                           'red': 0b00000001,
                           'green': 0b00000010,
                           'cyan': 0b00000100,
                           'teal': 0b00001000,
                           'blue': 0b00010000,
                           'violet': 0b00100000}
        self.current_index = 0

        self.channel_dict = {'bf': {'exciterSate': 'phase', 'exposure': 25, 'intensity': {'Intensity': 24}},
                             'green': {'exciterSate': 'cyan', 'exposure': 20, 'intensity': {'Cyan_Level': 20}},
                             'red': {'exciterSate': 'green', 'exposure': 100, 'intensity': {'Green_Level': 50}}}

        for key, name in mmDeviceName.items():
            self.__dict__[key] = mmDevice(name, self.mmCore)

        self.acq_state = False
        self.img_shape = None
        self.img_depth = None
        self.img_buff = None
        self.live_flag = False
        self.current_channel = 'Custom'
        if napri_inst is None:
            self.napari = Rand_camera()
        else: 
            self.napari = napri_inst
        self.stopAcq()

    def set_channel(self, channel_name):

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
        return self.trigger.ONTime / 1000

    @exposure.setter
    def exposure(self, exposure_time):
        """
        Set expsure time in ms
        """
        self.trigger.ONTime = exposure_time * 1000

    def initAcq(self):
        if self.mmCore.is_sequence_running():
            self.mmCore.stop_sequence_acquisition()
        else:
            self.mmCore.prepare_sequence_acquisition(self.camera.device_name)

        self.mmCore.clear_circular_buffer()
        self.mmCore.start_continuous_sequence_acquisition(1)
        self._get_img_info()
        self.acq_state = True

    def stopAcq(self):
        if self.mmCore.is_sequence_running():
            self.mmCore.stop_sequence_acquisition()
        self.mmCore.clear_circular_buffer()
        self.trigger.stop_trigger_continuously()
        self.acq_state = False

    def snap(self, show=False) -> tuple:
        """

        Performance: set exposure time, 8 models of light, 879 ms ± 39.6 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
        100 ms on channel

        Returns
        --------------
        img, imgtag: np.ndarray, dict
            (snape image, image info)
        """
        if not self.acq_state:
            self.initAcq()
        # image_in_buffer = self.mmCore.get_remaining_image_count()
        # self.mmCore.clear_circular_buffer()
        self.trigger.trigger_one_pulse()
        while True:
            if self.mmCore.get_remaining_image_count() == 1:
                break
            time.sleep(0.001)
        jv_img = self.mmCore.pop_next_tagged_image()
        image = jv_img.pix.reshape(self.img_shape)
        imgtag = jv_img.tags
        if show:
            self.img_buff = jv_img.pix.reshape(self.img_shape)
            self.napari.open_viewer()
            self.napari.update_layer((self.img_buff, self.current_channel))

        return image, imgtag

    def continuous_acq(self, duration_time: float, step: float, live=False):
        """
        :param live:
        :param duration_time: duration time, how long will acquisition lasting. unit: ms
        :param step: time interval. unit: ms
        """
        self._get_img_info()

        one_step_time = self.trigger.ONTime + self.trigger.OFFTime
        if one_step_time > step * 1000:
            self.trigger.FrameRate = 1000. / step
        else:
            self.trigger.OFFTime = int(step * 1000 - self.trigger.ONTime)
        one_step_time = self.trigger.ONTime + self.trigger.OFFTime
        frame_num = int(duration_time*1000 / one_step_time)
        # create a buffer
        self.img_buff = np.zeros((round(frame_num), *self.img_shape), dtype=self.img_depth)

        if not self.acq_state:
            self.initAcq()
        print('start acq!')
        self.trigger.trigger_continuously()

        if live:
            self.napari.open_viewer()
            self.napari.update_index_from_AcqTrigger(self)
            # while self.acq_state:
            #     time.sleep(1)
        else:
            im_count = 0
            self.current_index = 0
            pbar = tqdm(total=frame_num)  # create progress bar
            while im_count < frame_num:
                _time_cur = time.time()
                while self.mmCore.get_remaining_image_count() == 0:
                    pass
                if self.mmCore.get_remaining_image_count() > 0:
                    self.img_buff[im_count, ...] = self.mmCore.pop_next_image().reshape(self.img_shape)
                    self.current_index = im_count
                    im_count += 1
                    pbar.update(1)
            self.trigger.stop_trigger_continuously()
            # self.mmCore.stop_sequence_acquisition()
            # while self.mmCore.get_remaining_image_count() != 0:
            #     self.img_buff[im_count, ...] = self.mmCore.pop_next_image().reshape(self.img_shape)
            #     self.current_index = im_count
            #     im_count += 1
            #     pbar.update(1)
            pbar.close()
            self.stopAcq()
        vedio = self.img_buff  # clean the buffer

        print(f'FPS: {1e6/one_step_time}')

        return vedio

    # def live(self, step: float = 25, buffer_size=300):
    #
    #     live_thread = thread.Thread(target=thread_live, args=(step, buffer_size, self))
    #     live_thread.start()
    #     return None

    def show_live(self):
        # self.img_shape = [np.zeros(self.img_shape, self.img_depth)]
        # @thread_worker(connect={'yielded': self.napari.update_layer})
        @thread_worker
        def _camera_image(obj, layer_name, verbose=False):
            print('start live!')
            if verbose:
                im_count = 0
            if self.napari._flag is None:
                self.napari._flag = True

            while obj.live_flag:
                while obj.mmCore.get_remaining_image_count() == 0:
                    time.sleep(0.0001)
                img = obj.mmCore.get_last_image().reshape(obj.img_shape)
                # obj.img_buff = obj.mmCore.pop_next_image().reshape(obj.img_shape)                    
                if verbose:
                    im_count += 1
                    print(im_count)
                yield (img, layer_name)
            print('Stop Live!')
            return None
     
        self.napari._flag = True
        if self.napari.napari_viewer is None:
            self.napari.napari_viewer = napari.Viewer()
            
        if not self.acq_state:
            self.initAcq()
        
        self.trigger.trigger_continuously()
        self.live_flag = True
        # _camera_image(self, 'Live')
        
        worker = _camera_image(self, 'Live', False)
        worker.yielded.connect(self.napari.update_layer)
        worker.start()
        # self.napari.start_live(self, channel_name='Live')
        return None
    
    
    def stop_live(self):
        self.live_flag = False
        self.napari._flag = False
        self.stopAcq()
        return None



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
            image_list = [file.split('.')[0] for file in os.listdir(self.dir) if file.split('.')[-1] == self.suffix]
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

        self.file_name = os.path.join(self.dir, f'{self.main_name}_{self.index}.{self.suffix}')
        self.meta['axes'] = self.axes
        tiff.imwrite(self.file_name, data=self.data, 
                     photometric='minisblack', 
                     metadata=self.meta, imagej=True)

        self.index += 1
        return None


class AcqControl:
    def __init__(self, mmDeviceName=None, mmCore=None):
        if mmDeviceName is None:
            mmDeviceName = {'z': 'TIZDrive', 'pfs_state': 'TIPFSStatus', 'pfs_offset': 'TIPFSOffset'}
        self.z = None  # type: Optional[mmDevice]
        self.pfs_state = None  # type: Optional[mmDevice]
        self.pfs_offset = None  # type: Optional[mmDevice]
        self.xy = PriorScan(com=4) # PriorScan(com=4) FakeAcq()

        self.xy_num = None
        self.z_num = None
        self.c_num = None
        self.t_num = None
        
        
        self.nd_recorder = NDRecorder()
        self.napari = Rand_camera(self)
        self.acqTrigger = AcqTrigger(mmCore=mmCore, napri_inst=self.napari)
        # self.acqTrigger.napari = self.napari  # rewrite Napari of trigger
        self.mmCore = mmCore
        self._current_position = 0
        for key, name in mmDeviceName.items():
            self.__dict__[key] = mmDevice(name, mmCore)

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
                self.mmCore.set_position(self.pfs_offset.device_name, fov['pfsoffset'][0])
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
            device_dict = dict(xy='prior_xy', z=self.z.device_name, pfsoffset=self.pfs_offset.device_name)  # type: dict
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
        self.nd_recorder.update_position(self._current_position, self.get_position_dict())
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


if __name__ == '__main__':
# %%
    scopeControl = AcqControl(mmCore=core)
    scopeControl.napari.open_xyz_control_panel()
    img_acq = scopeControl.acqTrigger

    # img_acq.trigger.stop_trigger_continuously()
    # img_acq.trigger.trigger_continuously()
    # img_acq.napari.open_viewer()

    # ================ Only Live =============#
    img_acq.set_channel('bf')
    img_acq.show_live()
    img_acq.stop_live()
    # ================ Only Snap =========#
    img_acq.set_channel('red')
    img_acq.snap(show=True)
    img_acq.set_channel('green')
    img_acq.snap(show=True)
    img_acq.set_channel('bf')
    img_acq.snap(show=True)
    # ================ Acq Video ==========#
    img_acq.set_channel('bf')
    _ = img_acq.continuous_acq(1000 * 20, 40, live=True)

    img_save = imgSave()
    # vedio = img_acq.live(30)
    images = []
    for color in img_acq.triggerMap.keys():
        img_acq.exciterSate = color
        img, tag = img_acq.snap()
        images.append(img)
    img_save.save(dir=r'./', name='temp.tiff', data=np.array(images), axes='CYX', meta=tag)

    allDevice = javaList(core.get_loaded_devices())
    cameraName = core.get_camera_device()
    FluoresceDeviceName = 'Spectra'
    phaseLightSourceName = 'TIDiaLamp'
    ni_fpga = NIFPGADevice(bitfile=r'device/NI_FPGA/myRIO_v6.lvbitx', resource='rio://172.22.11.2/RIO0')
    camera = mmDevice(cameraName, core)
    spectraX = mmDevice(FluoresceDeviceName, core)
    dia = mmDevice(phaseLightSourceName, core)

    spectraX.load_device_property(r'./cfg_folder/Spectra_cfg_2023-05-26-14-10.json')
    camera.load_device_property(r'./cfg_folder/TUCam_cfg_2023-05-26-14-27.json')

    ni_fpga.ONTime = 100000
    ni_fpga.OFFTime = 10000

    # ni_fpga.set_outputpinmap(0b00000100)  # blue light
    # ni_fpga.set_outputpinmap(0b00000010)  # yellow light

    ni_fpga.set_outputpinmap(0b01000000)  # phase
    # ni_fpga.SequenceSize = 2
    # ni_fpga.PinArray = [int(0b01000000), int(0b00000100), 0, 0, 0, 0, 0, 0]
    # ni_fpga.Sequence = True
    ni_fpga.Synchronization = True
    # ni_fpga.trigger_continuously()
    # ni_fpga.FrameRate = 20


    # about image acq
    if core.is_sequence_running():
        core.stop_sequence_acquisition()
    core.clear_circular_buffer()
    core.prepare_sequence_acquisition(camera.device_name)
    core.start_continuous_sequence_acquisition(0)
    ni_fpga.trigger_continuously()
    disp = studio.live()

    if not disp.is_live_mode_on():
        disp.set_live_mode_on(True)
        window = disp.get_display()
    window.show()
    # ni_fpga.trigger_one_pulse()


    # ni_fpga.stop_trigger_continuously()
    if core.is_sequence_running():
        core.stop_sequence_acquisition()
        core.clear_circular_buffer()
    ni_fpga.stop_trigger_continuously()
    disp.set_live_mode(False)
