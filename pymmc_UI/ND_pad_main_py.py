# -*- coding: utf-8 -*-

"""

 @author: Pan M. CHU
 @Email: pan_chu@outlook.com
"""
#%%
# Built-in/Generic Imports
import os
import sys
# […]

# Libs
import pandas as pd
import numpy as np  # Or any other
# […]

# Own modules

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile
from pymmc_UI.pymmc_ND_pad import Ui_MainWindow


class NDRecorderUI(QMainWindow):
    def __init__(self):
        super(NDRecorderUI, self).__init__()
        self.ui = Ui_MainWindow
        self.ui.setupUi(self)

#%%
if __name__ == "__main__":
#%%
    app = QApplication(sys.argv)

    window = NDRecorderUI()
    window.show()

    sys.exit(app.exec())