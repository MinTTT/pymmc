# -*- coding: utf-8 -*-

"""
 @auther: Pan M. CHU
"""

# # Built-in/Generic Imports
# import os
# import sys
# # […]
#
# # Libs
# import pandas as pd
# import numpy as np  # Or any other
# # […]
import pymm as mm
global core
core = mm.core
# Own modules


class Microscope_Paras:
    def __init__(self, MICROSCOPE):
        self.MICROSCOPE = MICROSCOPE
        if self.MICROSCOPE == 'Ti2E':
            self.SHUTTER_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'XCite-Exacte'
            self.FILTER_TURRET = 'FilterTurret1'
            self.FLU_EXCITE = 'XCite-Exacte'
            self.GREEN_EXCITE = 15
            self.RED_EXCITE = 50
        elif self.MICROSCOPE == 'Ti2E_H':
            self. SHUTTER_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'Spectra'
            self.FILTER_TURRET = 'LudlWheel'
            self.GREEN_EXCITE = 15
            self.RED_EXCITE = 50
        elif self.MICROSCOPE == 'Ti2E_H_DB':
            self. SHUTTER_LAMP = 'DiaLamp'
            self.SHUTTER_LED = 'Spectra'
            self.FILTER_TURRET = 'FilterTurret1'
            self.GREEN_EXCITE = 15
            self.RED_EXCITE = 50
    def set_light_path(self, core_mmc, shift_type):
        """
        This function is used to set light from green to red channel.
        For Ti2E, two devices shall be changed their states. 1. FilterTurret, filter states
        :param core_mmc: mmcore
        :param shift_type: str, 'g2r' or 'r2g'
        :param micro_device: str, which device? 'Ti2E' or 'Ti2E_H'.
        :return: None
        """
        if self.MICROSCOPE == 'Ti2E':
            if shift_type == 'init_phase':
                pass
            if shift_type == "g2r":
                core_mmc.set_property(self.FILTER_TURRET, 'State', 5)  # set filer in 5 pos
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity', self.RED_EXCITE)  # set xcite lamp intensity 50
                mm.waiting_device()
            if shift_type == "r2g":
                core_mmc.set_property(self.FILTER_TURRET, 'State', 2)  # set filer in 2 pos
                core_mmc.set_property(self.FLU_EXCITE, 'Lamp-Intensity', self.GREEN_EXCITE)  # set xcite lamp intensity 2
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
                core_mmc.set_property(self.FILTER_TURRET, 'State', 2)
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
