# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 14:08:37 2020

@author: cheng
"""
#%%
import os
import time
from pyfirmata import Arduino, util
board = Arduino('com4')
while True:
    board.digital[13].write(1)
    time.sleep(10)
    board.digital[13].write(0)
    time.sleep(10)