# -*- coding: utf-8 -*-

"""
 @auther: Pan M. CHU
"""

import os
import time



# Own modules
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def test_thread(thread):
    while True:
        print(1)
        if not thread[0]:
            print('finish')
            break
        time.sleep(2)
    return None


def get_filenameindex(fold_name):
    file_list = os.listdir(fold_name)
    tiff_file = [int(name.split('.')[0][1:]) for name in file_list if
                 name.split('.')[-1] == 'tiff' and name.split('.')[0][0] == 't']
    return max(tiff_file) + 1
