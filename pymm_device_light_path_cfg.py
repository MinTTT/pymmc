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
from pymm_uitls import colors
colors = colors()
# global core
# core = mm.core
# Own modules


class MicroscopeParas:
    def __init__(self, MICROSCOPE):
        self.MICROSCOPE = MICROSCOPE
        if self.MICROSCOPE == 'Ti2E':
            self.SHUTTER_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'XCite-Exacte'
            self.FILTER_TURRET = 'FilterTurret1'
            self.FLU_EXCITE = 'XCite-Exacte'
            self.GREEN_EXCITE = 15
            self.RED_EXCITE = 50
            self.EXPOSURE_GREEN = 50  # 50 ms TiE2
            self.EXPOSURE_PHASE = 20  # ms
            self.EXPOSURE_RED = 200  # ms
            self.AUTOFOCUS_DEVICE = 'PFS'
            self.XY_DEVICE = 'XYStage'
        elif self.MICROSCOPE == 'TiE':
            self.SHUTTER_LAMP = 'Arduino-Shutter'
            self.INIT_LAMP = 'TIDiaLamp'
            self.SHUTTER_LED = 'XCite-Exacte'
            self.FILTER_TURRET = 'TIFilterBlock1'
            self.FLU_EXCITE = 'XCite-Exacte'
            self.GREEN_EXCITE = 15
            self.RED_EXCITE = 50
            self.EXPOSURE_GREEN = 50  # 50 ms TiE2
            self.EXPOSURE_PHASE = 20  # ms
            self.EXPOSURE_RED = 200  # ms
            self.AUTOFOCUS_DEVICE = 'TIPFSStatus'
            self.XY_DEVICE = 'XYStage'
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
        else:
            print(f'{colors.WARNING}{self.MICROSCOPE}: No such device tag!{colors.ENDC}')

    def set_light_path(self, core_mmc, shift_type):
        """
        This function is used to set light from green to red channel.
        For Ti2E, two devices shall be changed their states. 1. FilterTurret, filter states
        :param core_mmc: mmcore
        :param shift_type: str, 'g2r' or 'r2g' set light path flag
        :param micro_device: str, which device? 'Ti2E' or 'Ti2E_H'.
        :return: None
        """
        if self.MICROSCOPE == 'Ti2E':
            if shift_type == 'init_phase':
                core_mmc.set_property(self.FILTER_TURRET, 'State', 2)  # set filer in 5 pos
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
        elif self.MICROSCOPE == 'Ti2E_LDJ':
            if shift_type == 'init_phase':
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
                pass
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
        elif self.MICROSCOPE == 'Ti2E_H_DB':
            if shift_type == 'init_phase':
                core_mmc.set_property(self.FILTER_TURRET, 'State', 0)
                mm.waiting_device()
            if shift_type == 'r2g':
                core_mmc.set_property(self.SHUTTER_LED, 'Cyan_Level', self.GREEN_EXCITE)
                core_mmc.set_property(self.SHUTTER_LED, 'Cyan_Enable', 1)
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Enable', 0)
                mm.waiting_device()
            if shift_type == 'g2r':
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Level', self.RED_EXCITE)
                core_mmc.set_property(self.SHUTTER_LED, 'Green_Enable', 1)
                core_mmc.set_property(self.SHUTTER_LED, 'Cyan_Enable', 0)
                mm.waiting_device()
        return None
