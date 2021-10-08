# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 14:08:37 2020

@author: cheng
"""
# %%
import os
import threading
import time
from pyfirmata import Arduino, util
import threading as thread
import numpy as np

thread_lock = threading.Lock()


class ValveController:

    def __init__(self, port: str = 'com4', digital: int = 13) -> None:
        self.com = port
        self.board = Arduino(self.com)
        self.digital = digital

    def valve_off(self, time_delay: list = None):
        """
        turn off the valve.
        :param time_delay: list, turn off the valve after specific time duration [hr, min, s]
        :return: None
        """
        if time_delay:
            ts = format_time2second(time_delay)
            thread.Thread(target=self.thread_of_valve, args=(False, ts)).start()
        else:
            self._off()
        return None

    def valve_on(self, time_delay: list = None):
        """
        turn on the valve.
        :param time_delay: list, turn on the valve after specific time duration [hr, min, s]
        :return: None
        """
        if time_delay:
            ts = format_time2second(time_delay)
            thread.Thread(target=self.thread_of_valve, args=(True, ts)).start()
        else:
            self._on()
        return None

    def _off(self):
        self.board.digital[self.digital].write(0)
        return None

    def _on(self):
        self.board.digital[self.digital].write(1)
        return None

    def thread_of_valve(self, state: bool, time_delay: float):
        if state:
            countdown(time_delay, step=1, msg='Valve will On', msg_finish='Valve ON.')
            self._on()
        else:
            countdown(time_delay, step=1, msg='Valve will OFF', msg_finish='Valve OFF.')
            self._off()


def format_time2second(time_fmt: list):
    factor = [60 * 60, 60, 1]
    ts = np.sum([i for i in map(np.multiply, factor, time_fmt)])
    return ts


def countdown(t, step=1, msg='sleeping', msg_finish: str=None):
    """
    a countdown timer print waiting time in second.
    :param trigger: list, a global trigger
    :param t: time lasting for sleeping
    :param step: the time step between the refreshment of screen.
    :param msg:
    :return: None
    """
    CRED = '\033[91m'
    # CGRE = '\033[92m'
    CEND = '\033[0m'
    _current_time = time.time()
    while time.time() - _current_time < t:
        mins, secs = divmod(t + _current_time - time.time(), 60)
        thread_lock.acquire()
        print(CRED + f"""{msg} for {int(mins)}:{int(secs)}.""" + CEND, end='\r')
        thread_lock.release()
        time.sleep(step)
    if msg_finish:
        print(CRED + f"{msg_finish}" + CEND, end='\r')
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
