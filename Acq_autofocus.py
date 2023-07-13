"""
This code used for acq TCXY

Micro-manager config: Fulab-TiE.cfg
"""

# %%
from Acq_module import AcqControl, imgSave, core
import numpy as np
import time
import pymm as mm
# from napari.qt.threading import create_worker, FunctionWorker
import threading
from pymm_uitls import countdown
import os

# %%
# % Init device
device_ctrl = AcqControl(mmCore=core)
trigger = device_ctrl.acqTrigger

# %%
# Time duration in Seconds
time_duration = 3600 * 5
time_step = 5 * 60
# save dir 
save_dir = r"D:\zjw\20230704_6_60XRedInit_L3strins_TimeLapse"
# Channel
channels_set = {'red': {'exciterSate': 'green', 'exposure': 200, 'intensity': {'Green_Level': 50}},
                'green': {'exciterSate': 'cyan', 'exposure': 40, 'intensity': {'Cyan_Level': 20}},
                'bf': {'exciterSate': 'phase', 'exposure': 30, 'intensity': {'Intensity': 24}}}

# Select pos

trigger.channel_dict = channels_set
trigger.set_channel('bf')
device_ctrl.napari.open_xyz_control_panel()
trigger.show_live()


# %%


class imageAutoFocus:
    def __init__(self, MSPCtrl: AcqControl,
                 image_score_func=None, z_range=(100, 2000), z_step=20,
                 score_threshold=482247000,
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
        self.z_step_threshold = 0.01
        self.image = None
        self.max_loops = 100

    def get_image(self):
        if self.ctrl.acqTrigger.live_flag:
            self.ctrl.acqTrigger.stop_live()
        self.image, _ = self.ctrl.acqTrigger.snap(show=True)
        return self.image

    def eval_score(self):
        self.get_image()
        if self.image_mask:
            score = self.image_score_func(self.image[self.image_mask])
        else:
            score = self.image_score_func(self.image)

        return score

    def move_motor(self, distance):

        self.ctrl.mmCore.set_position(self.ctrl.z.device_name,
                                      self.get_current_z() + distance)
        mm.waiting_device()
        return None

    def get_current_z(self):
        return self.ctrl.mmCore.get_position(self.ctrl.z.device_name)

    def simaple_AF_func(self):
        current_score = self.eval_score()
        loop_num = 0
        direction = 1
        step_size = self.z_step
        step_thresh = self.z_step_threshold
        # climb, baby, climb!

        prev = current_score
        print(prev)
        while step_size > step_thresh:
            while loop_num < self.max_loops:

                print(direction * step_size, self.get_current_z())
                self.move_motor(direction * step_size)

                curr = self.eval_score()
                print(curr)
                # if curr > self.score_threshold:
                #     print("tres focused")
                #     return None

                diff = curr - prev
                curdir = 1 if diff > 0 else -1
                next_step = direction * step_size
                if next_step + self.get_current_z() > self.z_max or \
                        next_step + self.get_current_z() < self.z_min:
                    curdir = -1
                direction = curdir * direction
                prev = curr
                loop_num += 1
                if curdir == -1:
                    #     print(next_step)
                    # self.move_motor(direction * step_size)
                    # mm.waiting_device()
                    # if self.score_threshold >= 999999:
                    #     self.score_threshold = prev  
                    break

            step_size = step_size * 0.6
        print('Focus finish')
        return None

    def simaple_AF(self):
        thread = threading.Thread(target=self.simaple_AF_func)
        thread.start()
        return None


AF = imageAutoFocus(MSPCtrl=device_ctrl, z_range=(3700, 3800), z_step=10)
AF.simaple_AF()
# trigger.show_live()


# %%
