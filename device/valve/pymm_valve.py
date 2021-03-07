# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 14:08:37 2020

@author: cheng
"""
# %%
import os
import time
from pyfirmata import Arduino, util


class ValveController:

    def __init__(self, port: str = 'com4', digital: int = 13) -> None:
        self.com = port
        self.board = Arduino(self.com)
        self.digital = digital

    def valve_off(self):
        self.board.digital[self.digital].write(0)
        return None

    def valve_on(self):
        self.board.digital[self.digital].write(1)
        return None


# def valve_control(com='com4', state=0):
#     '''
#     Control WisperValve
#     :param com: com series name
#     :param state: state, int, if 0 NO, 1 NC
#     :return:
#     '''
#     board = Arduino(com)
#     board.digital[13].write(state)
#     return None

if __name__ == '__mian__':
    board = Arduino('com4')
    while True:
        board.digital[13].write(1)
        time.sleep(10)
        board.digital[13].write(0)
        time.sleep(10)
