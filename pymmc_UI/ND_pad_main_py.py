# -*- coding: utf-8 -*-

"""

 @author: Pan M. CHU
 @Email: pan_chu@outlook.com
"""
# %%
# Built-in/Generic Imports
import os
import sys
sys.path.append('../')
# […]

# Libs
# […]

# Own modules
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QShortcut
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
# from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QShortcut
# from PySide2.QtCore import Qt
# from PySide2.QtGui import QKeySequence
# import PySide2
from pymmc_UI.pymmc_ND_pad_pyqt5 import Ui_MainWindow
from random import random
from typing import Optional
from functools import partial
import threading


class FakeAcq:
    def __init__(self):
        self._positions = [{'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]},
                           {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]},
                           {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]}]
        self._current_position = len(self.positions) - 1
        # self.ND_ui = None
        # self.ND_app = None
        # self.nd_ui = NDRecorderUI(self)

    @property
    def positions(self):
        return self._positions

    @positions.setter
    def positions(self, pos_list):
        self._positions = pos_list

    @property
    def current_position(self) -> Optional[int]:
        return self._current_position

    def record_current_position(self):
        pos = {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]}
        self.positions.append(pos)
        self._current_position = len(self.positions) - 1
        return pos

    def record_current_position(self):
        pos = {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]}
        self.positions.append(pos)
        self._current_position = len(self.positions) - 1
        return pos

    def update_current_position(self):
        pos = {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]}
        print(pos)
        return pos

    def go_to_position(self, index):
        print(self.positions[index])
        self._current_position = index

    def move_right(self, dist: float = 127, convert=False):
        pos = {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]}
        if convert:
            pos['xy'][0] -= dist
        else:
            pos['xy'][0] += dist
        print(pos)

    def move_left(self, dist: float = 127, convert=False):
        pos = {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]}
        if convert:
            pos['xy'][0] += dist
        else:
            pos['xy'][0] -= dist
        print(pos)

    def move_up(self, dist: float = 127, convert=False):
        pos = {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]}
        if convert:
            pos['xy'][1] -= dist
        else:
            pos['xy'][1] += dist
        print(pos, 'up')

    def move_down(self, dist: float = 127, convert=False):
        pos = {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]}
        if convert:
            pos['xy'][1] += dist
        else:
            pos['xy'][1] -= dist
        print(pos)

    def remove_positions(self, pos_index):
        for i in sorted(pos_index, reverse=True):
            del self.positions[i]

    # def open_NDUI(self, test_flag=True):
    #     def open_in_subprocess(obj, testFlag):
    #         # app = QApplication(sys.argv)
    #         if not QApplication.instance():
    #             obj.ND_app = QApplication(sys.argv)
    #             obj.ND_ui = NDRecorderUI(obj, test=testFlag)
    #             obj.ND_ui.show()
    #             obj.ND_app.exec_()
    #         else:
    #             obj.ND_ui.show()
    #             obj.ND_app.exec_()
    #             # app = QApplication.instance()
    #             # ui = NDRecorderUI(obj, test=testFlag)
    #             # ui.show()
    #             # app.exec_()
    #         # ui = NDRecorderUI(obj, test=testFlag)
    #         # ui.show()
    #         # app.exec_()


    #     worker = threading.Thread(target=open_in_subprocess, args=(self, test_flag))
    #     worker.start()




class NDRecorderUI(QMainWindow, Ui_MainWindow):
    def __init__(self, acq_obj: FakeAcq, test: bool = False):
        self.acq_obj = acq_obj
        super(NDRecorderUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.pos_table = self.ui.ND_table
        self.update_button = self.ui.update
        self.ui.right_step.setValue(150)
        self.ui.left_step.setValue(150)
        self.ui.up_step.setValue(150)
        self.ui.down_step.setValue(150)
        self.ui.record_position.clicked.connect(self.do_record_pos)
        self.pos_table.itemClicked.connect(self.row_title_clicked)
        self.update_button.clicked.connect(self.do_update_pos)
        self.selected_index = []
        if test:
            self.positions = self.acq_obj.positions  # in test mode, manuplates positions 
        else:
            self.positions = self.acq_obj.nd_recorder.positions
        self.ui.move_up.clicked.connect(partial(self.move_xy, 'up'))
        self.ui.move_down.clicked.connect(partial(self.move_xy, 'down'))
        self.ui.move_right.clicked.connect(partial(self.move_xy, 'right'))
        self.ui.move_left.clicked.connect(partial(self.move_xy, 'left'))
        self.ui.delete_pos.clicked.connect(self.del_pos)

        # self.right_move = QShortcut(QKeySequence("Right"), self)
        # self.right_move.activated.connect(partial(self.move_xy, 'right'))
        #
        # self.left_move = QShortcut(QKeySequence("Left"), self)
        # self.left_move.activated.connect(partial(self.move_xy, 'left'))

        keydict = dict(right=["Right", partial(self.move_xy, 'right')],
                       left=["Left", partial(self.move_xy, 'left')],
                       up=['Up', partial(self.move_xy, 'up')],
                       down=['Down', partial(self.move_xy, 'down')],
                       record=['Space', self.do_record_pos],
                       update=["U", self.do_update_pos])
        self.bound_shortcut(keydict)

        self.write_table()

    def bound_shortcut(self, key_dict):
        for key, val in key_dict.items():
            self.__dict__[f'{key}_st'] = QShortcut(QKeySequence(val[0]), self)
            self.__dict__[f'{key}_st'].activated.connect(val[1])

    def write_table(self):
        self.pos_table.clear()
        self.pos_table.setRowCount(len(self.positions))
        for row, pos in enumerate(self.positions):
            self.edit_row(row, pos)

    def edit_row(self, row_index: int, pos: dict):
        row_count = self.pos_table.rowCount()
        # add a new line
        if row_index >= row_count - 1:
            self.pos_table.setRowCount(row_index + 1)
        # add the element
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
        check_box = QTableWidgetItem('select')
        check_box.setCheckState(Qt.Unchecked)
        self.pos_table.setItem(row_index, 4, check_box)

    def do_record_pos(self):
        pos = self.acq_obj.record_current_position()
        print(pos)
        self.edit_row(self.acq_obj.current_position, pos)

    def do_update_pos(self):
        pos = self.acq_obj.update_current_position()
        self.edit_row(self.acq_obj.current_position, pos)

    def row_title_clicked(self, item):
        row = self.pos_table.currentRow()
        column = self.pos_table.currentColumn()
        if self.ui.checkBox_2.isChecked():
            self.acq_obj.go_to_position(row)

    def move_xy(self, direction: str):
        if direction == 'left':
            self.acq_obj.move_left(dist=float(self.ui.left_step.value()))
        elif direction == 'right':
            self.acq_obj.move_right(dist=float(self.ui.right_step.value()))
        elif direction == 'up':
            self.acq_obj.move_up(dist=float(self.ui.up_step.value()))
        elif direction == 'down':
            self.acq_obj.move_down(dist=float(self.ui.down_step.value()))

    def del_pos(self):
        del_index = [i for i in range(self.pos_table.rowCount()) if
                     self.pos_table.item(i, 4).checkState() == Qt.Checked]

        self.acq_obj.remove_positions(del_index)

        self.pos_table.clear()
        self.write_table()


# %%
if __name__ == "__main__":
    # %%
    acq_loop = FakeAcq()
    acq_loop.open_NDUI(True)

    # if not QApplication.instance():
    #     app = QApplication(sys.argv)
    # else:
    #     app = QApplication.instance()


    # window = NDRecorderUI(acq_loop, test=True)



    # window.show()
    # app.exec()



# %%

