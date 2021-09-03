# -*- coding: utf-8 -*-

"""

 @author: Pan M. CHU
 @Email: pan_chu@outlook.com
"""
# %%
# Built-in/Generic Imports
import os
import sys
# […]

# Libs
import pandas as pd
import numpy as np  # Or any other
# […]

# Own modules
import PySide6.QtWidgets as QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtCore import QFile
from pymmc_UI.pymmc_ND_pad import Ui_MainWindow
from random import random


class FakeAcq:
    def __init__(self):
        self.positions = []
        self._current_position = None

    def record_current_position(self):
        pos = {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]}
        self.positions.append(pos)
        self._current_position = len(self.positions) - 1
        return pos


class NDRecorderUI(QMainWindow):
    def __init__(self, acq_obj: FakeAcq):
        self.acq_obj = acq_obj
        super(NDRecorderUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.pos_table = self.ui.ND_table

        self.ui.record_position.clicked.connect(self.do_record_pos)
        self.pos_table.itemClicked.connect(self.row_title_clicked)

    def edit_row(self, row_index, pos):
        row_count = self.pos_table.rowCount()
        if row_index >= row_count - 1:
            self.pos_table.setRowCount(row_index + 1)

        for key, val in pos.items():
            if key == 'xy':
                data1, data2 = QTableWidgetItem(str('%.3f' % val[0])), QTableWidgetItem(str('%.3f' % val[1]))
                self.pos_table.setItem(row_index, 0, data1)
                self.pos_table.setItem(row_index, 1, data2)
            if key == 'z':
                data = QTableWidgetItem('%.3f' % val[0])
                self.pos_table.setItem(row_index, 2, data)
            if key == 'pfsoffset':
                data = QTableWidgetItem('%.3f' % val[0])
                self.pos_table.setItem(row_index, 3, data)

    def do_record_pos(self):
        pos = self.acq_obj.record_current_position()
        print(pos)
        self.edit_row(self.acq_obj._current_position, pos)

    def row_title_clicked(self, item):
        row = self.pos_table.currentRow()
        column = self.pos_table.currentColumn()
        if self.ui.checkBox_2.isChecked():
            print(f'we will move! ({row}, {column})')





# %%
if __name__ == "__main__":
    # %%
    acq_loop = FakeAcq()
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    window = NDRecorderUI(acq_loop)
    window.show()
    app.exec()
    # sys.exit(app.exec())
