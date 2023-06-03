# -*- coding: utf-8 -*-

"""
 @author: Pan M. CHU
"""

from ctypes import WinDLL, create_string_buffer, c_int, POINTER, c_char

import os
import sys
import time


def load_sdk(ps):
    if os.path.exists(ps):
        return WinDLL(ps)
    else:
        raise RuntimeError("DLL could not be loaded.")


class PriorScan(object):
    def __init__(self, com=8, dll_path=r"./device/prior_stage/x64/PriorScientificSDK.dll"):
        """
        :param com: int, com port number, if COM3, use the value 3
        :param dll_path: str, default use dll in this project
        """
        self.com = com
        self.dll_ps = dll_path
        self.SDKPrior = load_sdk(self.dll_ps)
        self.rx = create_string_buffer(50000)
        self.rx_decode = None
        self._cmd = self.SDKPrior.PriorScientificSDK_cmd
        self._cmd.argtypes = (c_int, POINTER(c_char), POINTER(c_char))
        self._cmd.restype = c_int
        # initialize
        self.ret = None
        self.session_id = None
        self.spermicro = None
        self.ss = 1  # step per step, default is 1
        self.device_list = ['xystage', 'filter']
        self.initialize()

    def __del__(self):
        self.close_session()

    def initialize(self):
        self.ret = self.SDKPrior.PriorScientificSDK_Initialise()
        if self.ret:
            raise RuntimeError(f"[Prior SDK]: Error initialising {self.ret}")
        else:
            print(f"[Prior SDK]: Ok initialising {self.ret}")
        self.ret = self.SDKPrior.PriorScientificSDK_Version(self.rx)
        print(f'[Prior SDK]: api version: {self.rx.value.decode()}')
        # session
        self.session_id = self.SDKPrior.PriorScientificSDK_OpenNewSession()
        if self.session_id < 0:
            # print(f'Error getting session ID {self.session_id}')
            # sys.exit()
            raise RuntimeError(f'[Prior SDK]: Error getting session ID {self.session_id}')
        self.ret = self.SDKPrior.PriorScientificSDK_cmd(
            self.session_id, create_string_buffer(f"controller.connect {self.com}".encode()), self.rx)
        if self.ret < 0:
            raise RuntimeError(f'[Prior SDK]: Error connecting COM{self.com}')

        # XY Stage get step per micro
        # self.ret = self.SDKPrior.PriorScientificSDK_cmd(
        #     self.session_id, create_string_buffer("controller.stage.steps-per-micron.get".encode()), self.rx)
        self.ret = self.cmd("controller.stage.steps-per-micron.get")
        self.spermicro = int(self.decode_rx())
        # set user step per step
        # self.ret = self.SDKPrior.PriorScientificSDK_cmd(
        #     self.session_id, create_string_buffer(f"controller.stage.ss.set {self.ss}".encode()), self.rx)
        self.ret = self.cmd(f"controller.stage.ss.set {self.ss}")
        self.initial_filter()

    def cmd(self, msg):
        self.ret = self._cmd(self.session_id, create_string_buffer(msg.encode()), self.rx)
        return self.rx.value.decode()

    def decode_rx(self):
        return self.rx.value.decode()

    # def steppermicro(self):
    #     self.rx_decode = self.cmd('controller.stage.steps-per-micron.get')
    #     self.spermicro = int(self.rx_decode)

    def device_busy(self, device='xystage') -> int:
        """
        get the busy status of the stage
        :return: 0 idle, 1 X moving, 2 Y moving, 3 both X and Y moving
        """
        if device == 'xystage':
            self.rx_decode = self.cmd("controller.stage.busy.get")
        if device == 'filter':
            self.rx_decode = self.cmd("controller.filter.busy.get")
        return int(self.rx_decode)

    def waiting_device(self, device: str = None):
        if device is None:
            states_list = [True] * len(self.device_list)
            while states_list:
                for dev in self.device_list:
                    if self.device_busy(dev) == 0:
                        _ = states_list.pop()
                time.sleep(0.1)
        else:
            states_list = [True]
            while states_list:
                if self.device_busy(device) == 0:
                    _ = states_list.pop()
                time.sleep(0.1)

    def get_xy_position(self) -> (float, float):
        """
        Returns the current stage XY position
        :return: float x um, float y um
        """
        rx_decode = self.cmd("controller.stage.position.get")
        x, y = rx_decode.split(',')
        return float(x) / self.spermicro, float(y) / self.spermicro

    def set_xy_position(self, x: float, y: float):
        xs, ys = int(self.spermicro * x), int(self.spermicro * y)
        self.rx_decode = self.cmd(f'controller.stage.goto-position {xs} {ys}')

    def set_shutter_state(self, state: int = 0, shutter_index: int = 1):
        if state == 0:
            self.rx_decode = self.cmd(f"controller.shutter.close {shutter_index}")
        else:
            self.rx_decode = self.cmd(f"controller.shutter.open {shutter_index}")

    def get_shutter_state(self, shutter_index: int = 1):
        rx_decode = self.cmd(f"controller.shutter.state.get {shutter_index}")
        return rx_decode

    def set_filter_position(self, pos: int, filter_index: int = 1):
        self.rx_decode = self.cmd(f'controller.filter.goto-position {filter_index} {pos}')

    def get_filter_position(self, filter_index: int = 1):
        self.rx_decode = self.cmd(f'controller.filter.position.get {filter_index}')
        return self.rx_decode

    def close_session(self):
        self.rx_decode = self.cmd("controller.disconnect")
        self.ret = self.SDKPrior.PriorScientificSDK_CloseSession(self.session_id)

    def set_filter_speed_acc(self, speed=None, acc=None, filter_index: int = 1):
        if speed is not None:
            self.rx_decode = self.cmd(f'controller.filter.speed.set {filter_index} {speed}')
        if acc is not None:
            self.rx_decode = self.cmd(f'controller.filter.acc.set {filter_index} {acc}')

    def get_filter_speed_acc(self, filter_index: int = 1):
        speed = self.rx_decode = self.cmd(f'controller.filter.speed.get {filter_index}')
        acc = self.rx_decode = self.cmd(f'controller.filter.acc.get {filter_index}')
        return speed, acc

    def initial_filter(self, set_default=True, pars={}):
        speed_acc_default = [50, 50]

        filter_device_dict = {}
        for filter_index in range(1, 7):
            filter_device_dict.update({filter_index: self.cmd(f"controller.filter.fitted.get {filter_index}") == '1'})
        if set_default:
            for filter_index, state in filter_device_dict.items():
                if state is True:
                    self.set_filter_speed_acc(*speed_acc_default, filter_index)
                    self.rx_decode = self.cmd(f'controller.filter.home {filter_index}')
        if pars:
            for filter_index, acc_speed in pars.items():
                self.set_filter_speed_acc(*acc_speed, filter_index)


# %%
if __name__ == '__main__':

    # %%
    conncet = PriorScan(com=4)
    # %%

    stage = PriorScan(com=8)
    os.chdir(r'D:\python_code\pymmc\device\prior_stage\x64/')
    path = "PriorScientificSDK.dll"
    if os.path.exists(path):
        SDKPrior = WinDLL(path)
    else:
        raise RuntimeError("DLL could not be loaded.")

    rx = create_string_buffer(50000)
    realhw = False

    _cmd = SDKPrior.PriorScientificSDK_cmd
    _cmd.argtypes = (c_int, POINTER(c_char), POINTER(c_char))
    _cmd.restype = c_int


    def cmd(msg):
        # print(msg)
        # ret = SDKPrior.PriorScientificSDK_cmd(
        #     sessionID, create_string_buffer(msg.encode()), rx
        # )
        ret = _cmd(sessionID, create_string_buffer(msg.encode()), rx)
        if ret:
            print(f"Api error {ret}")
        else:
            print(f"OK {rx.value.decode()}")

        # input("Press ENTER to continue...")
        return ret, rx.value.decode()


    # %%
    ret = SDKPrior.PriorScientificSDK_Initialise()
    if ret:
        print(f"Error initialising {ret}")
        sys.exit()
    else:
        print(f"Ok initialising {ret}")

    # %%
    ret = SDKPrior.PriorScientificSDK_Version(rx)
    print(f"dll version api ret={ret}, version={rx.value.decode()}")

    sessionID = SDKPrior.PriorScientificSDK_OpenNewSession()
    if sessionID < 0:
        print(f"Error getting sessionID {ret}")
    else:
        print(f"SessionID = {sessionID}")
    # %%

    ret = SDKPrior.PriorScientificSDK_cmd(
        sessionID, create_string_buffer(b"dll.apitest 33 goodresponse"), rx
    )
    print(f"api response {ret}, rx = {rx.value.decode()}")
    input("Press ENTER to continue...")

    ret = SDKPrior.PriorScientificSDK_cmd(
        sessionID, create_string_buffer(b"dll.apitest -300 stillgoodresponse"), rx
    )
    print(f"api response {ret}, rx = {rx.value.decode()}")
    input("Press ENTER to continue...")

    # %%
    if realhw:
        print("Connecting...")
        # substitute 3 with your com port Id
        cmd("controller.connect 6")

        # test an illegal command
        cmd("controller.stage.position.getx")

        # get current XY position in default units of microns
        cmd("controller.stage.position.get")

        # re-define this current position as 1234,5678
        cmd("controller.stage.position.set 1234 5678")

        # check it worked
        cmd("controller.stage.position.get")

        # set it back to 0,0
        cmd("controller.stage.position.set 0 0")
        cmd("controller.stage.position.get")

        # start a move to a new position, normally you would poll
        # 'controller.stage.busy.get' until response = 0
        cmd("controller.stage.goto-position 1234 5678")

        # example velocity move of 10u/s in both x and y
        cmd("controller.stage.move-at-velocity 10 10")

        # see busy status
        cmd("controller.stage.busy.get")

        # stop velocity move
        cmd("controller.stage.move-at-velocity 0 0")

        # see busy status */
        cmd("controller.stage.busy.get")

        # see new position
        cmd("controller.stage.position.get")

        # disconnect cleanly from controller
        cmd("controller.disconnect")

    else:
        input("Press ENTER to continue...")
