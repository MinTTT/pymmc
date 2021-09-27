# -*- coding: utf-8 -*-

"""
 @auther: Pan M. CHU
"""

# # Built-in/Generic Imports
# import os
# import sys
# # […]

# # Libs
# import pandas as pd
# import numpy as np  # Or any other
# # […]
import pymm as mm
from pymm import save_image
from pymm_uitls import colors
import time
import numpy as np
from device.prior_device import PriorScan
from typing import Optional
from device.arduino import ARDUINO
colors = colors()

# global core
mmcore = mm.core


# Own modules


class MicroscopeParas:
    def __init__(self, MICROSCOPE, CAM_ROI=None):
        self.MICROSCOPE = MICROSCOPE
        if self.MICROSCOPE == 'Ti2E':
            self.SHUTTER_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'XCite-Exacte'
            self.FILTER_TURRET = 'FilterTurret1'
            self.FLU_EXCITE = 'XCite-Exacte'
            self.GREEN_EXCITE = 15
            self.RED_EXCITE = 50
            self.EXPOSURE_GREEN = 100  # 50 ms TiE2
            self.EXPOSURE_PHASE = 20  # ms
            self.EXPOSURE_RED = 200  # ms
            self.AUTOFOCUS_DEVICE = 'PFS'
            self.XY_DEVICE = 'XYStage'
            self.Z_DEVICE = 'ZDrive'
            self.AUTOFOCUS_OFFSET = 'PFSOffset'
            self.mmcore = mmcore
        elif self.MICROSCOPE == 'TiE':
            self.SHUTTER_LAMP = 'Arduino-Shutter'
            self.INIT_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'XCite-Exacte'
            self.FILTER_TURRET = 'TIFilterBlock1'
            self.FLU_EXCITE = 'XCite-Exacte'
            self.GREEN_EXCITE = 15
            self.RED_EXCITE = 50
            self.EXPOSURE_GREEN = 50  # 50 ms TiE2
            self.EXPOSURE_PHASE = 40  # ms
            self.EXPOSURE_RED = 200  # ms
            self.AUTOFOCUS_DEVICE = 'PFSStatus'
            self.AUTOFOCUS_OFFSET = 'PFSOffset'
            self.Z_DEVICE = 'ZDrive'
            self.XY_DEVICE = 'XYStage'
            self.mmcore = mmcore
        elif self.MICROSCOPE == 'TiE_prior':
            self.SHUTTER_LAMP = 'Arduino-Shutter'
            self.INIT_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'XCite-Exacte'
            self.FILTER_TURRET = 'FilterBlock1'
            self.FLU_EXCITE = 'XCite-Exacte'
            # =================== version 1. ====================
            # self.GREEN_EXCITE = 15
            # self.RED_EXCITE = 50  # 50 for 100X cfg, 100 for 60X cfg
            # self.EXPOSURE_GREEN = 50  # 50 ms TiE2
            # self.EXPOSURE_PHASE = 30  # 30 ms for 60X
            # self.EXPOSURE_RED = 50  # ms
            # =================== version 2. ====================
            self.GREEN_EXCITE = 8
            self.RED_EXCITE = 25  # 50 for 100X cfg, 100 for 60X cfg
            self.EXPOSURE_GREEN = 25  # 50 ms TiE2
            self.EXPOSURE_PHASE = 30  # 30 ms for 60X
            self.EXPOSURE_RED = 25  # ms
            self.AUTOFOCUS_DEVICE = 'PFSStatus'
            self.AUTOFOCUS_OFFSET = 'PFSOffset'
            self.Z_DEVICE = 'ZDrive'
            self.XY_DEVICE = 'prior_xy'
            self.mmcore = mmcore
            self.prior_core = None  # type: Optional[PriorScan]
        elif self.MICROSCOPE == 'TiE_prior_arduino':
            self.SHUTTER_LAMP = 'Arduino'
            self.INIT_LAMP = 'DiaLamp'
            self.FILTER_TURRET = 'FilterBlock1'
            self.FLU_EXCITE = 'XCite-Exacte'
            self.GREEN_EXCITE = 8
            self.RED_EXCITE = 25  # 50 for 100X cfg, 100 for 60X cfg
            self.EXPOSURE_GREEN = 25  # 50 ms TiE2
            self.EXPOSURE_PHASE = 30  # 30 ms for 60X
            self.EXPOSURE_RED = 25  # ms
            self.AUTOFOCUS_DEVICE = 'PFSStatus'
            self.AUTOFOCUS_OFFSET = 'PFSOffset'
            self.Z_DEVICE = 'ZDrive'
            self.XY_DEVICE = 'prior_xy'
            self.mmcore = mmcore
            self.prior_core = None  # type: Optional[PriorScan]
            self.arduino_core = None  # type: Optional[ARDUINO]
        elif self.MICROSCOPE == 'TiE_prior_DNA_replicate':
            self.SHUTTER_LAMP = 'Arduino-Shutter'
            self.INIT_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'XCite-Exacte'
            self.FILTER_TURRET = 'FilterBlock1'
            self.FLU_EXCITE = 'XCite-Exacte'
            self.YELLOW_EXCITE = 50
            self.EXPOSURE_YELLOW = 100
            self.EXPOSURE_PHASE = 30  # 30 ms for 60X
            self.AUTOFOCUS_DEVICE = 'PFSStatus'
            self.AUTOFOCUS_OFFSET = 'PFSOffset'
            self.Z_DEVICE = 'ZDrive'
            self.XY_DEVICE = 'prior_xy'
            self.mmcore = mmcore
            self.prior_core = None  # type: Optional[PriorScan]
        elif self.MICROSCOPE == 'Ti2E_H':
            self.SHUTTER_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'Spectra'
            self.FILTER_TURRET = 'LudlWheel'
            self.GREEN_EXCITE = 15
            self.RED_EXCITE = 50
            self.EXPOSURE_GREEN = 50  # 50 ms TiE2
            self.EXPOSURE_PHASE = 20  # ms
            self.EXPOSURE_RED = 200  # ms
            self.AUTOFOCUS_DEVICE = 'PFS'
            self.XY_DEVICE = 'XYStage'
            self.Z_DEVICE = 'ZDrive'
            self.mmcore = mmcore
        elif self.MICROSCOPE == 'Ti2E_H_4C':
            self.SHUTTER_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'Spectra'
            self.FILTER_TURRET = 'LudlWheel'
            self.TURRET = 'FilterTurret1'
            self.GREEN_EXCITE = 15
            self.RED_EXCITE = 50
            self.BLUE_EXCITE = 15
            self.EXPOSURE_GREEN = 50  # 50 ms TiE2
            self.EXPOSURE_PHASE = 20  # ms
            self.EXPOSURE_RED = 200  # ms
            self.EXPOSURE_BLUE = 20
            self.EXPOSURE_YELLOW = 20
            self.YELLOW_EXCITE = 15
            self.AUTOFOCUS_DEVICE = 'PFS'
            self.XY_DEVICE = 'XYStage'
            self.Z_DEVICE = 'ZDrive'
            self.AUTOFOCUS_OFFSET = 'PFSOffset'
            self.mmcore = mmcore
        elif self.MICROSCOPE == 'Ti2E_H_DB':
            self.SHUTTER_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'Spectra'
            self.FILTER_TURRET = 'FilterTurret1'
            self.GREEN_EXCITE = 15
            self.RED_EXCITE = 50
            self.EXPOSURE_GREEN = 50  # 50 ms TiE2
            self.EXPOSURE_PHASE = 20  # ms
            self.EXPOSURE_RED = 200  # ms
            self.AUTOFOCUS_DEVICE = 'PFS'
            self.XY_DEVICE = 'XYStage'
            self.Z_DEVICE = 'ZDrive'
            self.mmcore = mmcore
        elif self.MICROSCOPE == 'Ti2E_LDJ':
            self.SHUTTER_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'XCite-Exacte'
            self.FLU_EXCITE = 'XCite-Exacte'
            self.FILTER_TURRET = 'FilterTurret1'
            self.GREEN_EXCITE = 15
            self.RED_EXCITE = 15
            self.EXPOSURE_GREEN = 100  # 50 ms TiE2
            self.EXPOSURE_PHASE = 20  # ms
            self.EXPOSURE_RED = 100  # ms
            self.AUTOFOCUS_DEVICE = 'PFS'
            self.XY_DEVICE = 'XYStage'
            self.Z_DEVICE = 'ZDrive'
            self.AUTOFOCUS_OFFSET = 'PFSOffset'
            self.mmcore = mmcore
        else:
            print(f'{colors.WARNING}{self.MICROSCOPE}: No such device tag!{colors.ENDC}')
        # initial func
        self.CAM_ROI = CAM_ROI
        self.set_light_path = None
        self.move_xyz_pfs = None
        self.autofocus = None
        self.auto_acq_save = None
        self.active_auto_shutter = None
        self.set_ROI = None
        self.init_func()

    def init_func(self):
        """
        initialize function, determine call MMCORE or DLL directly
        :return:
        """
        self.set_light_path = mm.set_light_path
        self.move_xyz_pfs = mm.move_xyz_pfs
        self.autofocus = mm.autofocus
        self.auto_acq_save = mm.auto_acq_save
        self.active_auto_shutter = mm.active_auto_shutter
        self.set_ROI = mm.mm_set_camer_roi

        if self.XY_DEVICE == 'prior_xy':

            self.prior_core = PriorScan()

            def move_xyz_pfs(fov, turnoffz=True, step=6, fov_len=133.3, core=self.mmcore):
                """
                Move stage xy and z position.
                :param fov:
                :param turnoffz: bool, if ture, microscope will keep the pfs working and skipping moving the z device.
                :return: None
                """
                x_f, y_f = self.prior_core.get_xy_position()
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
                    self.prior_core.set_xy_position(x_space[i + 1], y_space[i + 1])
                    while self.prior_core.device_busy():
                        time.sleep(0.0001)
                if turnoffz:
                    if 'pfsoffset' in fov:
                        core.set_position(self.AUTOFOCUS_OFFSET, fov['pfsoffset'][0])
                else:
                    if 'z' in fov:
                        core.set_position(self.Z_DEVICE, fov['z'][0])
                    mm.waiting_device()
                return None

            self.move_xyz_pfs = move_xyz_pfs

        if self.SHUTTER_LAMP == 'Arduino':
            self.arduino_core = ARDUINO()

        if self.MICROSCOPE in ['TiE_prior_arduino']:

            def save_and_acq(im_dir: str, name: str, exposure: float, shutter=None):
                """
                auto acquisition image and save.

                :param im_dir: str, path
                :param name: str, image name
                :param exposure: float, set exposure time
                :param shutter: None or str, if None, microscope use current shutter
                :return: None
                """
                if shutter is not None:
                    active_auto_shutter(shutter)
                im, meta = snap_image(exposure=exposure)
                thread.start_new_thread(save_image, (im, im_dir, name, meta))
                return None


    def get_position_dict(self, device: Optional[str] = None) -> dict:
        """
        get current position
        :param device: None or string, if device not given, return all devices' positions
        :return: a dict containing positions
        """
        pos = {}
        if device == None:
            device_dict = dict(xy=self.XY_DEVICE, z=self.Z_DEVICE, pfsoffset=self.AUTOFOCUS_OFFSET)  # type: dict
            for key, dev in device_dict.items():
                if dev == 'prior_xy':
                    pos[key] = list(self.prior_core.get_xy_position())
                else:
                    value = self.mmcore.get_position(dev)
                    if isinstance(value, float) or isinstance(value, int):
                        pos[key] = [value]
                    else:
                        pos[key] = value
        return pos

    def auto_focus(self, z: float = None, pfs: float = None):
        if self.MICROSCOPE in ['TiE', 'TiE_prior']:
            z = 3262
            z_init = z - 50
            z_top = 4000
            z_bottom = z_init
            psf_val = 128.7
            self.mmcore.set_position(self.AUTOFOCUS_OFFSET, psf_val)
            while not self.mmcore.is_continuous_focus_locked():
                self.mmcore.set_position(self.Z_DEVICE, z_init)
                delta_z = self.mmcore.get_position(self.Z_DEVICE) - z_init
                if delta_z > 5:
                    z_init = self.mmcore.get_position(self.Z_DEVICE) + 0.1
                # elif -10 > delta_z:
                #     z_init = self.mmcore.get_position(self.Z_DEVICE)
                else:
                    z_init += 8
                # while not self.mmcore.is_continuous_focus_enabled():
                #     time.sleep(0.1)
                #     self.mmcore.enable_continuous_focus(True)

                # while mmcore.device_busy(self.Z_DEVICE):
                #     time.sleep(0.001)
                if z_init > z_top:
                    z_init = z - 100
                if z_init < z_bottom:
                    z_init = z_bottom

    def check_auto_focus(self, lag=0.1):
        """
        make sure that the pfs is locked

        :return:
        """
        while not self.mmcore.is_continuous_focus_locked():
            while not self.mmcore.is_continuous_focus_enabled():
                self.mmcore.enable_continuous_focus(True)
                time.sleep(lag)
        return None

    def set_device_state(self, core_mmc=None, shift_type=None):
        """
        This function is used to set light from green to red channel.
        For Ti2E, two devices shall be changed their states. 1. FilterTurret, filter states
        :param core_mmc: mmcore
        :param shift_type: str, 'g2r' or 'r2g' set light path flag
        :param micro_device: str, which device? 'Ti2E' or 'Ti2E_H'.
        :return: None
        """
        if core_mmc == None:
            core_mmc = self.mmcore

        if self.MICROSCOPE == 'Ti2E':
            if shift_type == 'init_phase':
                core_mmc.set_property(self.FILTER_TURRET, 'State', 2)  # set filer in 5 pos
                if self.CAM_ROI is not None:
                    self.set_ROI(self.CAM_ROI)
                mm.waiting_device()
            if shift_type == "g2r":
                core_mmc.set_property(self.FILTER_TURRET, 'State', 1)  # set filer in 5 pos
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity', self.RED_EXCITE)  # set xcite lamp intensity 50
                mm.waiting_device()
            if shift_type == "r2g":
                core_mmc.set_property(self.FILTER_TURRET, 'State', 2)  # set filer in 2 pos
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity',
                                      self.GREEN_EXCITE)  # set xcite lamp intensity 2
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity',
                                      self.GREEN_EXCITE)  # set xcite lamp intensity 2
                mm.waiting_device()
        elif self.MICROSCOPE == 'TiE':
            if shift_type == 'init_phase':
                if self.CAM_ROI is not None:
                    self.set_ROI(self.CAM_ROI)
                core_mmc.set_property(self.INIT_LAMP, 'State', 1)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 2)
                mm.waiting_device()
            if shift_type == "g2r":
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity', self.RED_EXCITE)  # set xcite lamp intensity 50
                core_mmc.set_property(self.FILTER_TURRET, 'State', 3)  # set filer in 3 pos
                mm.waiting_device()
            if shift_type == "r2g":
                core_mmc.set_property(self.FILTER_TURRET, 'State', 2)  # set filer in 2 pos
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity',
                                      self.GREEN_EXCITE)  # set xcite lamp intensity 2
                mm.waiting_device()
        elif self.MICROSCOPE == 'TiE_prior':
            if shift_type == 'init_phase':
                if self.CAM_ROI is not None:
                    self.set_ROI(self.CAM_ROI)
                core_mmc.set_property(self.INIT_LAMP, 'State', 1)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 5)
                self.prior_core.set_shutter_state(1)
                self.prior_core.set_filter_position(3)
                mm.waiting_device()
                self.prior_core.waiting_device()
            if shift_type == "g2r":
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity', self.RED_EXCITE)  # set xcite lamp intensity 50
                core_mmc.set_property(self.FILTER_TURRET, 'State', 5)  # set filer in 3 pos
                self.prior_core.set_filter_position(4)
                mm.waiting_device()
                self.prior_core.waiting_device()
            if shift_type == "r2g":
                core_mmc.set_property(self.FILTER_TURRET, 'State', 5)  # set filer in 2 pos
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity',
                                      self.GREEN_EXCITE)  # set xcite lamp intensity 2
                self.prior_core.set_filter_position(3)
                mm.waiting_device()
                self.prior_core.waiting_device()

        elif self.MICROSCOPE == 'TiE_prior_arduino':
            if shift_type == 'init_phase':
                if self.CAM_ROI is not None:
                    self.set_ROI(self.CAM_ROI)
                self.arduino_core.trigger_pattern = 32
                self.arduino_core.start_blanking_mode()
                core_mmc.set_property(self.INIT_LAMP, 'State', 1)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 5)
                self.prior_core.set_shutter_state(1)
                self.prior_core.set_filter_position(3)
                mm.waiting_device()
                self.prior_core.waiting_device()

            if shift_type == "g2r":
                self.arduino_core.trigger_pattern = 16
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity', self.RED_EXCITE)  # set xcite lamp intensity 50
                core_mmc.set_property(self.FILTER_TURRET, 'State', 5)  # set filer in 3 pos
                self.prior_core.set_filter_position(4)
                mm.waiting_device()
                self.prior_core.waiting_device()

            if shift_type == "r2g":
                core_mmc.set_property(self.FILTER_TURRET, 'State', 5)  # set filer in 2 pos
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity',
                                      self.GREEN_EXCITE)  # set xcite lamp intensity 2
                self.prior_core.set_filter_position(3)
                mm.waiting_device()
                self.prior_core.waiting_device()

            if shift_type == 'phase':
                self.arduino_core.trigger_pattern = 32
            if shift_type == 'fluorescent':
                self.arduino_core.trigger_pattern = 16


        elif self.MICROSCOPE == 'Ti2E_LDJ':
            if shift_type == 'init_phase':
                if self.CAM_ROI is not None:
                    self.set_ROI(self.CAM_ROI)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 3)
                mm.waiting_device()
            if shift_type == 'r2g':
                core_mmc.set_property(self.FILTER_TURRET, 'State', 3)  # set filer in 3 pos YFP
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity',
                                      self.GREEN_EXCITE)  # set xcite lamp intensity 50
                mm.waiting_device()
            if shift_type == 'g2r':
                core_mmc.set_property(self.FILTER_TURRET, 'State', 1)  # set filer in 5 pos
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity', self.RED_EXCITE)  # set xcite lamp intensity 50
                mm.waiting_device()
        elif self.MICROSCOPE == 'Ti2E_H':
            if shift_type == 'init_phase':
                if self.CAM_ROI is not None:
                    self.set_ROI(self.CAM_ROI)
            if shift_type == "r2g":
                core_mmc.set_property(self.SHUTTER_LED, 'Cyan_Level', self.GREEN_EXCITE)
                core_mmc.set_property(self.SHUTTER_LED, 'Cyan_Enable', 1)
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Enable', 0)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 3)  # pos 3 521
                mm.waiting_device()
            if shift_type == 'g2r':
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Level', self.RED_EXCITE)
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Enable', 1)
                core_mmc.set_property(self.SHUTTER_LED, 'Cyan_Enable', 0)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 5)  # pos5 631/36
                mm.waiting_device()
        elif self.MICROSCOPE == 'Ti2E_H':
            if shift_type == 'init_phase':
                if self.CAM_ROI is not None:
                    self.set_ROI(self.CAM_ROI)
            if shift_type == "r2g":
                core_mmc.set_property(self.SHUTTER_LED, 'Cyan_Level', self.GREEN_EXCITE)
                core_mmc.set_property(self.SHUTTER_LED, 'Cyan_Enable', 1)
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Enable', 0)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 3)  # pos 3 521
                mm.waiting_device()
            if shift_type == 'g2r':
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Level', self.RED_EXCITE)
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Enable', 1)
                core_mmc.set_property(self.SHUTTER_LED, 'Cyan_Enable', 0)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 5)  # pos5 631/36
                mm.waiting_device()
        elif self.MICROSCOPE == 'Ti2E_H_4C':
            if shift_type == 'init_phase':
                if self.CAM_ROI is not None:
                    self.set_ROI(self.CAM_ROI)
                core_mmc.set_property(self.TURRET, 'State', 3)
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Enable', 0)
                core_mmc.set_property(self.SHUTTER_LED, 'Blue_Enable', 0)
                core_mmc.set_property(self.SHUTTER_LED, 'Teal_Enable', 0)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 2)
                mm.waiting_device()
            if shift_type == '3t1':
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Enable', 0)
                core_mmc.set_property(self.SHUTTER_LED, 'Blue_Level', self.BLUE_EXCITE)
                core_mmc.set_property(self.SHUTTER_LED, 'Blue_Enable', 1)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 2)
                mm.waiting_device()
            if shift_type == '1t2':
                core_mmc.set_property(self.SHUTTER_LED, 'Blue_Enable', 0)
                core_mmc.set_property(self.SHUTTER_LED, 'Teal_Level', self.YELLOW_EXCITE)
                core_mmc.set_property(self.SHUTTER_LED, 'Teal_Enable', 1)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 8)
                mm.waiting_device()
            if shift_type == '2t3':
                core_mmc.set_property(self.SHUTTER_LED, 'Teal_Enable', 0)
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Level', self.RED_EXCITE)
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Enable', 1)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 7)
                mm.waiting_device()
            if shift_type == '3t2':
                core_mmc.set_property(self.SHUTTER_LED, 'Teal_Enable', 1)
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Level', self.YELLOW_EXCITE)
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Enable', 0)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 8)
            if shift_type == '2t1':
                core_mmc.set_property(self.SHUTTER_LED, 'Blue_Enable', 1)
                core_mmc.set_property(self.SHUTTER_LED, 'Teal_Level', self.BLUE_EXCITE)
                core_mmc.set_property(self.SHUTTER_LED, 'Teal_Enable', 0)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 2)
                mm.waiting_device()

        elif self.MICROSCOPE == 'TiE_prior_DNA_replicate':
            if shift_type == 'init_phase':
                if self.CAM_ROI is not None:
                    self.set_ROI(self.CAM_ROI)
                core_mmc.set_property(self.INIT_LAMP, 'State', 1)
                core_mmc.set_property(self.FILTER_TURRET, 'State', 4)
                self.prior_core.set_shutter_state(1)
                self.prior_core.set_filter_position(1)
                mm.waiting_device()
                self.prior_core.waiting_device()
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity',
                                      self.YELLOW_EXCITE)  # set xcite lamp intensity 50
        return None


if __name__ == 'main':
    # %%
    dev = MicroscopeParas('TiE')
    dev.auto_focus()
