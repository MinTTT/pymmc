# -*- coding: utf-8 -*-

"""
 @author: Pan M. CHU
"""

from ctypes import WinDLL, create_string_buffer, c_int, POINTER, c_char

import os
import sys


def load_sdk(ps):
    if os.path.exists(ps):
        return WinDLL(ps)
    else:
        raise RuntimeError("DLL could not be loaded.")


class PriorScan(object):
    def __init__(self, com=6, dll_path=r"./device/prior_stage/x64/PriorScientificSDK.dll"):
        """
        :param com: int, com port number, if COM3, use the value 3
        :param dll_path: str, default use dll in this project
        """
        self.com = com
        self.dll_ps = dll_path
        self.SDKPrior = load_sdk(self.dll_ps)
        self.rx = create_string_buffer(5000)
        self.rx_decode = None
        self._cmd = self.SDKPrior.PriorScientificSDK_cmd
        self._cmd.argtypes = (c_int, POINTER(c_char), POINTER(c_char))
        self._cmd.restype = c_int
        # initialize
        self.ret = None
        self.session_id = None
        self.spermicro = None
        self.ss = 1  # step per step, default is 1
        self.initialize()

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

    def cmd(self, msg):
        self.ret = self._cmd(self.session_id, create_string_buffer(msg.encode()), self.rx)
        return self.rx.value.decode()

    def decode_rx(self):
        return self.rx.value.decode()

    # def steppermicro(self):
    #     self.rx_decode = self.cmd('controller.stage.steps-per-micron.get')
    #     self.spermicro = int(self.rx_decode)

    def device_busy(self) -> int:
        """
        get the busy status of the stage
        :return: 0 idle, 1 X moving, 2 Y moving, 3 both X and Y moving
        """
        self.rx_decode = self.cmd("controller.stage.busy.get")
        return int(self.rx_decode)

    def get_xy_position(self) -> (float, float):
        """
        Returns the current stage XY position
        :return: float x um, float y um
        """
        self.rx_decode = self.cmd("controller.stage.position.get")
        x, y = self.rx_decode.split(',')
        return float(x) / self.spermicro, float(y) / self.spermicro

    def set_xy_position(self, x: float, y: float):
        xs, ys = int(self.spermicro * x), int(self.spermicro * y)
        self.rx_decode = self.cmd(f'controller.stage.goto-position {xs} {ys}')

    def close_session(self):
        self.rx_decode = self.cmd("controller.disconnect")
        self.ret = self.SDKPrior.PriorScientificSDK_CloseSession(self.session_id)


# %%
if __name__ == '__main__':

    #%%
    conncet = PriorScan(com=6)
    #%%

    stage = PriorScan(com=6)
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
