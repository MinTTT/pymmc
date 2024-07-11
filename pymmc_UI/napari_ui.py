"""
@author: CHU Pan
@email: pan_chu@outlook.com
"""
#%%
import os
from tkinter import N
import numpy as np
import time
from napari.qt.threading import thread_worker
import tifffile as tif
from tqdm import tqdm
import Acq_parameters as acq_paras
import warnings
import napari
import sys

from typing import Optional
import threading
# from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QShortcut, QWidget
# from PySide2.QtCore import Qt, QObject
# from PySide2.QtGui import QKeySequence
# from pymmc_UI.pymmc_ND_pad import Ui_MainWindow
from napari.window import Window
from random import random
from functools import partial
from typing import Optional
import os
import sys

# import imp
sys.path.append(r'../')
from magicgui import widgets
import napari
# from napari.qt.threading import FunctionWorker, thread_worker
# from napari.types import ImageData, LayerDataTuple
#
# from skimage import data
import numpy as np
import time
from threading import Thread
from napari.qt.threading import thread_worker
from typing import Optional, Annotated


class FakeAcq:
    def __init__(self):
        self._positions = [{'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]},
                           {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]},
                           {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]}]
        self._current_position = len(self.positions) - 1

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

    # def record_current_position(self):
    #     pos = {'xy': [random(), random()], 'z': [random()], 'pfsoffset': [random()]}
    #     self.positions.append(pos)
    #     self._current_position = len(self.positions) - 1
    #     return pos

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

    def get_xy_position(self, ):
        return [random(), random()]

    def set_xy_position(self, xy):
        print(f'Go to xy {xy}')

    def device_busy(self, ):

        time.sleep(.1)
        return False

    # def open_NDUI(self):
    #     def open_in_subprocess(obj):
    #         if not QApplication.instance():
    #             app = QApplication(sys.argv)
    #         else:
    #             app = QApplication.instance()
    #         ui = NDRecorderUI(obj)
    #         ui.show()
    #         app.exec()

    #     threading.Thread(target=open_in_subprocess, args=(self,)).start()
#%%
from magicgui import magicgui
import datetime
import pathlib

@magicgui(
    call_button="Calculate",
    slider_float={"widget_type": "FloatSlider", 'max': 10},
    dropdown={"choices": ['first', 'second', 'third']},
)
def widget_demo(
    maybe: bool,
    some_int: int,
    spin_float=3.14159,
    slider_float=4.5,
    string="Text goes here",
    dropdown='first',
    date=datetime.datetime.now(),
    filename=pathlib.Path('/some/path.ext')
):
    pass

widget_demo.show()
#%%
# class NDRecorderUI(QMainWindow, Ui_MainWindow):
#     def __init__(self, acq_obj, test: bool = False):
#         """
#         Connect UI action to device
#         """
#         self.acq_obj = acq_obj
#         super(NDRecorderUI, self).__init__()
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)
#         if test:
#             self.positions = self.acq_obj.positions
#             print('Test Mode ON.')
#         else:
#             self.positions = self.acq_obj.nd_recorder.positions
#             print('Loading ND Recorder')
#         self.pos_table = self.ui.ND_table
#         self.update_button = self.ui.update
#         self.ui.right_step.setValue(150)
#         self.ui.left_step.setValue(150)
#         self.ui.up_step.setValue(150)
#         self.ui.down_step.setValue(150)
#         self.ui.record_position.clicked.connect(self.do_record_pos)
#         self.pos_table.itemClicked.connect(self.row_title_clicked)
#         self.update_button.clicked.connect(self.do_update_pos)
#         self.selected_index = []
#         self.ui.move_up.clicked.connect(partial(self.move_xy, 'up'))
#         self.ui.move_down.clicked.connect(partial(self.move_xy, 'down'))
#         self.ui.move_right.clicked.connect(partial(self.move_xy, 'right'))
#         self.ui.move_left.clicked.connect(partial(self.move_xy, 'left'))
#         self.ui.delete_pos.clicked.connect(self.del_pos)


#         keydict = dict(right=["Right", partial(self.move_xy, 'right')],
#                        left=["Left", partial(self.move_xy, 'left')],
#                        up=['Up', partial(self.move_xy, 'up')],
#                        down=['Down', partial(self.move_xy, 'down')],
#                        record=['Space', self.do_record_pos],
#                        update=["U", self.do_update_pos])
#         self.bound_shortcut(keydict)

#         self.write_table()

#     def bound_shortcut(self, key_dict):
#         for key, val in key_dict.items():
#             self.__dict__[f'{key}_st'] = QShortcut(QKeySequence(val[0]), self)
#             self.__dict__[f'{key}_st'].activated.connect(val[1])

#     def write_table(self):
#         self.pos_table.clear()
#         self.pos_table.setRowCount(len(self.positions))
#         for row, pos in enumerate(self.positions):
#             self.edit_row(row, pos)

#     def edit_row(self, row_index: int, pos: dict):
#         row_count = self.pos_table.rowCount()
#         # add a new line
#         if row_index >= row_count - 1:
#             self.pos_table.setRowCount(row_index + 1)
#         # add the element
#         for key, val in pos.items():
#             if key == 'xy':
#                 data1, data2 = QTableWidgetItem(str('%.3f' % val[0])), QTableWidgetItem(str('%.3f' % val[1]))
#                 self.pos_table.setItem(row_index, 0, data1)
#                 self.pos_table.setItem(row_index, 1, data2)
#             if key == 'z':
#                 data = QTableWidgetItem('%.3f' % val[0])
#                 self.pos_table.setItem(row_index, 2, data)
#             if key == 'pfsoffset':
#                 data = QTableWidgetItem('%.3f' % val[0])
#                 self.pos_table.setItem(row_index, 3, data)
#         check_box = QTableWidgetItem('select')
#         check_box.setCheckState(Qt.Unchecked)
#         self.pos_table.setItem(row_index, 4, check_box)


#     def do_record_pos(self):

#         @thread_worker
#         def recored_pos(obj):
#             pos = obj.acq_obj.record_current_position()
#             print(pos)
#             obj.edit_row(obj.acq_obj.current_position, pos)

#         worker = recored_pos(self)
#         worker.start()
#         # pos = self.acq_obj.record_current_position()
#         # print(pos)
#         # self.edit_row(self.acq_obj.current_position, pos)
#         return None


#     def do_update_pos(self):
#         pos = self.acq_obj.update_current_position()
#         self.edit_row(self.acq_obj.current_position, pos)

#     def row_title_clicked(self, item):
#         row = self.pos_table.currentRow()
#         column = self.pos_table.currentColumn()
#         if self.ui.checkBox_2.isChecked():
#             self.acq_obj.go_to_position(row)

#     def move_xy(self, direction: str):
#         if direction == 'left':
#             self.acq_obj.move_left(dist=float(self.ui.left_step.value()))
#         elif direction == 'right':
#             self.acq_obj.move_right(dist=float(self.ui.right_step.value()))
#         elif direction == 'up':
#             self.acq_obj.move_up(dist=float(self.ui.up_step.value()))
#         elif direction == 'down':
#             self.acq_obj.move_down(dist=float(self.ui.down_step.value()))

#     def del_pos(self):
#         del_index = [i for i in range(self.pos_table.rowCount()) if
#                      self.pos_table.item(i, 4).checkState() == Qt.Checked]

#         self.acq_obj.remove_positions(del_index)

#         self.pos_table.clear()
#         self.write_table()


# class NDRecorderUI(QMainWindow, Ui_MainWindow):
#     def __init__(self, acq_obj, test: bool = False):
#         """
#         Connect UI action to device
#         """
#         self.acq_obj = acq_obj
#         super(NDRecorderUI, self).__init__()

#         self.setupUi(self)
#         if test:
#             self.positions = self.acq_obj.positions
#             print('Test Mode ON.')
#         else:
#             self.positions = self.acq_obj.nd_recorder.positions
#             print('Loading ND Recorder')
#         self.pos_table = self.ND_table
#         self.update_button = self.update
#         self.right_step.setValue(150)
#         self.left_step.setValue(150)
#         self.up_step.setValue(150)
#         self.down_step.setValue(150)
#         self.record_position.clicked.connect(self.do_record_pos)
#         self.pos_table.itemClicked.connect(self.row_title_clicked)
#         self.update_button.clicked.connect(self.do_update_pos)
#         self.selected_index = []
#         self.move_up.clicked.connect(partial(self.move_xy, 'up'))
#         self.move_down.clicked.connect(partial(self.move_xy, 'down'))
#         self.move_right.clicked.connect(partial(self.move_xy, 'right'))
#         self.move_left.clicked.connect(partial(self.move_xy, 'left'))
#         self.delete_pos.clicked.connect(self.del_pos)

#         keydict = dict(right=["Right", partial(self.move_xy, 'right')],
#                        left=["Left", partial(self.move_xy, 'left')],
#                        up=['Up', partial(self.move_xy, 'up')],
#                        down=['Down', partial(self.move_xy, 'down')],
#                        record=['Space', self.do_record_pos],
#                        update=["U", self.do_update_pos])
#         self.bound_shortcut(keydict)

#         self.write_table()
#         print(f'{self.acq_obj.get_position_dict()}')

#     def bound_shortcut(self, key_dict):
#         for key, val in key_dict.items():
#             self.__dict__[f'{key}_st'] = QShortcut(QKeySequence(val[0]), self)
#             self.__dict__[f'{key}_st'].activated.connect(val[1])

#     def write_table(self):
#         self.pos_table.clear()
#         self.pos_table.setRowCount(len(self.positions))
#         for row, pos in enumerate(self.positions):
#             self.edit_row(row, pos)

#     def edit_row(self, row_index: int, pos: dict):
#         row_count = self.pos_table.rowCount()
#         # add a new line
#         if row_index >= row_count - 1:
#             self.pos_table.setRowCount(row_index + 1)
#         # add the element
#         for key, val in pos.items():
#             if key == 'xy':
#                 data1, data2 = QTableWidgetItem(str('%.3f' % val[0])), QTableWidgetItem(str('%.3f' % val[1]))
#                 self.pos_table.setItem(row_index, 0, data1)
#                 self.pos_table.setItem(row_index, 1, data2)
#             if key == 'z':
#                 data = QTableWidgetItem('%.3f' % val[0])
#                 self.pos_table.setItem(row_index, 2, data)
#             if key == 'pfsoffset':
#                 data = QTableWidgetItem('%.3f' % val[0])
#                 self.pos_table.setItem(row_index, 3, data)
#         check_box = QTableWidgetItem('select')
#         check_box.setCheckState(Qt.Unchecked)
#         self.pos_table.setItem(row_index, 4, check_box)

#     def do_record_pos(self):

#         # @thread_worker
#         # def recored_pos(obj):
#         #     pos = obj.acq_obj.record_current_position()
#         #     print(pos)
#         #     obj.edit_row(obj.acq_obj.current_position, pos)

#         # worker = recored_pos(self)
#         # worker.start()
#         pos = self.acq_obj.record_current_position()
#         print(pos)
#         self.edit_row(self.acq_obj.current_position, pos)
#         return None

#     def do_update_pos(self):
#         pos = self.acq_obj.update_current_position()
#         self.edit_row(self.acq_obj.current_position, pos)

#     def row_title_clicked(self, item):
#         row = self.pos_table.currentRow()
#         column = self.pos_table.currentColumn()
#         if self.checkBox_2.isChecked():
#             self.acq_obj.go_to_position(row)

#     def move_xy(self, direction: str):
#         if direction == 'left':
#             self.acq_obj.move_left(dist=float(self.left_step.value()))
#         elif direction == 'right':
#             self.acq_obj.move_right(dist=float(self.right_step.value()))
#         elif direction == 'up':
#             self.acq_obj.move_up(dist=float(self.up_step.value()))
#         elif direction == 'down':
#             self.acq_obj.move_down(dist=float(self.down_step.value()))

#     def del_pos(self):
#         del_index = [i for i in range(self.pos_table.rowCount()) if
#                      self.pos_table.item(i, 4).checkState() == Qt.Checked]

#         self.acq_obj.remove_positions(del_index)

#         self.pos_table.clear()
#         self.write_table()


# class Rand_camera:
#     def __init__(self, xyz_controller=None, imsize=(2048, 2048), depth=np.uint16):
#         self.xyz_controller = xyz_controller
#         self._image_size = imsize
#         self._depth = depth
#         self._flag = None
#         self.napari_viewer = None  # type: Optional[napari.Viewer]
#         self._img_gen = None
#         self.colormap_set = {'green': 'green', 'red': 'red', 'bf': 'gray'}
#         self.xyzPanelwindow = None

#     def open_viewer(self):
#         try:
#             if self.napari_viewer is None:
#                 self.napari_viewer = napari.Viewer()
#             # self.napari_viewer.show()
#             napari.run()
#         except RuntimeError:
#             self.napari_viewer = napari.Viewer()
#             # self.napari_viewer.run()
#             napari.run()
#         return None

#     def open_xyz_control_panel(self):
#         if self.xyz_controller:

#             self.open_viewer()

#             self.xyzPanelwindow = NDRecorderUI(self.xyz_controller, test=False)
#             self.xyzPanelwindow.show()
#             napari.run()
#         else:
#             warnings.warn("XYZ Controller isn't detected.")

#     def start_live(self, obj, channel_name):
#         @thread_worker(connect={'yielded': self.update_layer})
#         def _camera_image(obj, layer_name):

#             im_count = 0
#             if self._flag is None:
#                 self._flag = True
#             try:
#                 while obj.live_flag:
#                     while obj.mmCore.get_remaining_image_count() == 0:
#                         time.sleep(0.001)

#                     img = obj.mmCore.get_last_image().reshape(obj.img_shape)
#                     # obj.img_buff = obj.mmCore.pop_next_image().reshape(obj.img_shape)                    
#                     im_count += 1
#                     print(im_count)
#                     yield (img, layer_name)
#             except:
#                 print('Some happen')

#             # obj.napari.stop_live()
#             # obj.trigger.stop_trigger_continuously()
#             # obj.mmCore.stop_sequence_acquisition()
#             # obj.stopAcq()
#             return None

#         self._flag = True
#         if self.napari_viewer is None:
#             self.napari_viewer = napari.Viewer()

#         if not obj.acq_state:
#             obj.initAcq()
#         print('start live!')
#         obj.trigger.trigger_continuously()
#         obj.live_flag = True
#         _camera_image(obj, channel_name)

#         # self.camera_live(obj, channel_name)
#         return None

#     def update_layer(self, args):
#         """
#         Parameters:
#             args: tuple
#                 (new_image, layerName)
#         """
#         new_image, layerName = args
#         try:
#             # if the layer exists, update the data
#             self.napari_viewer.layers[layerName].data = new_image
#         except KeyError:
#             # otherwise add it to the viewer
#             try:
#                 cmap = self.colormap_set[layerName]
#             except KeyError:
#                 cmap = 'gray'
#             self.napari_viewer.add_image(new_image,
#                                          name=layerName,
#                                          blending='additive',
#                                          colormap=cmap)
#         return None

#     def stop_live(self):
#         self._flag = False

#     def large_random_images(self):
#         @thread_worker(connect={'yielded': self.update_layer})
#         def _large_random_images():
#             if self._flag is None:
#                 self._flag = True

#             random_img = (np.random.random(self._image_size) * 2 ** 16).astype(self._depth)
#             while self._flag:
#                 time.sleep(.01)
#                 random_img = (np.random.random(self._image_size) * 2 ** 16).astype(self._depth)
#                 yield random_img
#             return random_img

#         _large_random_images()

#     def update_vedio_layers(self, args):
#         """

#         :param args: (new_imgs, layerindex, layername)
#         :return:
#         """
#         new_imgs, layerindex, layername = args
#         try:
#             # if the layer exists, update the data
#             self.napari_viewer.layers[layername].data = new_imgs
#         except KeyError:
#             # otherwise add it to the viewer
#             self.napari_viewer.add_image(new_imgs, name=layername)
#         self.napari_viewer.dims.set_point(0, layerindex)
#         return None

#     def update_index_from_AcqTrigger(self, obj):
#         @thread_worker(connect={'yielded': self.update_layer})
#         def _update_index(obj):
#             im_count = 0
#             obj.current_index = 0
#             pbar = tqdm(total=len(obj.img_buff))  # create progress bar
#             while im_count < len(obj.img_buff):
#                 _time_cur = time.time()
#                 while obj.mmCore.get_remaining_image_count() == 0:
#                     pass
#                 if obj.mmCore.get_remaining_image_count() > 0:
#                     obj.img_buff[im_count, ...] = obj.mmCore.pop_next_image().reshape(obj.img_shape)
#                     yield obj.img_buff[im_count, ...], obj.current_channel
#                     obj.current_index = im_count
#                     im_count += 1
#                     pbar.update(1)

#             obj.trigger.stop_trigger_continuously()
#             obj.stopAcq()
#             pbar.close()
#             yield obj.img_buff, obj.current_channel
#             return None

#         _update_index(obj)

#         return None

#     def update_index(self, args):
#         """
#         update image index
#         :param args: (axis, index)
#         :return:
#         """
#         axis, index = args
#         self.napari_viewer.dims.set_point(axis, index)
#         return None

#     def acq_random_images(self, duration_time, step, im_name, dir):
#         frame_num = round(duration_time / step)
#         img_buffer = np.empty(shape=(frame_num, *self._image_size)).astype(self._depth)
#         self.open_viewer()

#         @thread_worker(connect={'yielded': self.update_vedio_layers})
#         def _acq_random_images(buffer, name, dir):
#             franme_num = buffer.shape[0]
#             for i in range(franme_num):
#                 time.sleep(step)
#                 random_img = (np.random.random(self._image_size) * 2 ** 16).astype(self._depth)
#                 buffer[i, ...] = random_img
#                 yield buffer, i, im_name
#             tif.imsave(os.path.join(dir, f'{name}.tiff'), buffer)
#             return None

#         _acq_random_images(img_buffer, im_name, dir)
#         return None

"""
magicgui with threadworker
==========================

An example of calling a threaded function from a magicgui ``dock_widget``.
Note: this example requires python >=m 3.9

.. tags:: gui
"""

#%%

# from pymmc_UI.ND_pad_main_py import FakeAcq
# from napari_ui import NDRecorderUI

def threaded(func):
    """
    Decorator that multithreads the target function
    with the given parameters. Returns the thread
    created for the function
    """

    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args)
        thread.start()
        return thread

    return wrapper

def minute2Time(minute: float):
    return '%i:%i:%.1f' % (minute // 60, minute % 60 // 1, minute % 60 % 1 * 60)

class microConfigManag:
    def __init__(self, config_dict=None,
                 UI: Optional[napari.Viewer] = None):
        if config_dict is None:
            config_dict = {}
        self.config_dict = config_dict
        self.UI = UI

    @property
    def config_names(self):
        return list(self.config_dict.keys())
    
    def get_config(self, name):
        return self.config_dict[name]

    def load_configs(self, config_dict: dict):
        for key, inst in config_dict.items():
            self.config_dict[key] = inst

    def load_config(self, name, config_dict: dict):
        for key, value in config_dict.items():
            self.config_dict[name][key] = value

    def manipulate_AcqControl(self):
        pass

    def manipulate_UI(self):
        pass


#%%

class randCamera:

    def __init__(self, buffer_size: int = 1, y_size: int = 512,
                 x_size: int = 512, time_step: float = 1) -> None:
        self.buffer_size = buffer_size
        self.y_size = y_size
        self.x_size = x_size
        self.time_step = time_step
        self.current_index: int = -1
        self.buffer = np.zeros((buffer_size, y_size, x_size), dtype=np.uint16)
        self.live_flag = False

    def snap(self) -> None:
        self.current_index = (self.current_index + 1) % self.buffer_size
        self.buffer[self.current_index, ...] = np.random.random((self.y_size, self.x_size)) * 2 ** 16
        return None

    @threaded
    def _live(self):
        self.live_flag = True
        while self.live_flag:
            self.current_index = (self.current_index + 1) % self.buffer_size
            self.buffer[self.current_index, ...] = np.random.random((self.y_size, self.x_size)) * 2 ** 16
            time.sleep(self.time_step / 1000)
        return 0

    def live(self):
        # worker = Thread(target=self._live, args=())
        # worker.start()
        worker = self._live()

    def live_stop(self):
        self.live_flag = False


# camera = randCamera(100, 512, 512)
# %%
# if __name__ == '__main__':
#     camera = Rand_camera()
#     for i in range(3):
#         imgs = camera.acq_random_images(20, 0.1, f'random vedio{i}', r'./')

# flag = [True]
#
# large_random_images(flag)  # call the function!
# np_viewer





class AcqViewer:
    
    def __init__(self, camera=None, triggerMap=None, acq_setup=None) -> None:
        self.viewer = napari.Viewer()
        if camera:
            self.camera = camera
        else:
            self.camera = randCamera(100, 512, 512)  # wrapper for provide images and controlling image acq
        if triggerMap:
            self.triggerMap = triggerMap
        else:
            self.triggerMap = acq_paras.trigger_map
        if acq_setup:
            self.acq_setup = acq_setup
        else:
            self.acq_setup = acq_paras.channels

        self.acq_config = microConfigManag(config_dict=self.acq_setup)  # microConfigManag helps to edit the values in acq_setup
        
        # GUI 1. live view
        triggerChoiceList = list(self.triggerMap.keys())
        self.acqSetUpChoice = widgets.Combobox(value=self.acq_config.config_names[1], 
                                          choices=self.acq_config.config_names, 
                                        label='Acquisition Setup')
        exposure_Time = dict(value=20., min=15., max=1000., step=1.)  # value, min, max, step
        self.intensityBar = widgets.FloatSlider(value=0., min=0., max=100., step=1, label='Intensity: ')
        self.startBottom = widgets.ToggleButton(text='Start/Stop Live', value=False)
        self.snapBottom = widgets.PushButton(text='Snap', value=False)
        self.triggerChoice = widgets.ComboBox(value=triggerChoiceList[0],
                                        choices=triggerChoiceList, label='Trigger type: ')
        self.exposureTime = widgets.FloatSpinBox(**exposure_Time, label='Exposure time (ms): ')
        self.configParsWidges = widgets.Container(widgets=[self.triggerChoice, self.exposureTime, self.intensityBar])
        self.liveGUI = widgets.Container(widgets=[self.acqSetUpChoice, self.configParsWidges,
                                            widgets.Container(widgets=[self.startBottom, self.snapBottom], layout='horizontal')])

        self.interconnect_change_guipars(self.acq_config.config_names[1])  # init all Acq parameters
        self.acqSetUpChoice.changed.connect(self.interconnect_change_guipars)
        self.startBottom.changed.connect(self.connect_triggerBottom)
        self.snapBottom.changed.connect(self.connect_snapBottom)
        self.triggerChoice.changed.connect(self.config_connect_change_exciterSate)
        self.exposureTime.changed.connect(self.config_connect_change_exposure)
        self.intensityBar.changed.connect(self.config_connect_change_intensity)

        # GUI 2. ND acq
        self.firstPhase = widgets.Container(widgets=[widgets.CheckBox(value=False, text=key) for key in self.acq_setup.keys()],
                                    label='1st phase', layout='horizontal')
        self.secondPhase = widgets.Container(widgets=[widgets.CheckBox(value=False, text=key) for key in self.acq_setup.keys()],
                                        label='2nd phase', layout='horizontal')
        self.firstPhaseNum = widgets.FloatSpinBox(value=1, min=1, step=1, label='1st phase number/loop: ')
        self.secondPhaseNum = widgets.FloatSpinBox(value=0, min=0, step=1, label='2nd phase number/loop: ')
        self.PhaseNum = widgets.Container(widgets=[self.firstPhaseNum, self.secondPhaseNum])
        self.LoopStep = widgets.Container(widgets=[widgets.FloatSpinBox(value=1, min=0, step=.1, label='Loop time Step (min): '),
                                            widgets.FloatSpinBox(value=1, min=1, step=1, label='Loop number: ')])

        self.estimateTime = widgets.Label(label='Estimate time: ')
        # calcEstimateTime()

        self.LoopStep.changed.connect(self.calcEstimateTime)
        self.PhaseNum.changed.connect(self.calcEstimateTime)
        self.PhaseNum.changed.connect(self.calcEstimateTime)

        # GUI 3. ND pad
        # acq_loop = FakeAcq()
        # NDSelectionUI = NDRecorderUI(acq_loop, test=True)
        # def show_NDSelectionUI():
        #     acq_loop.open_NDUI(test_flag=True)

        self.NDSelectionBottom = widgets.PushButton(text='Open location selection', value=False)
        # NDSelectionBottom.changed.connect(show_NDSelectionUI)

        # GUI 4. save direct
        self.dirSelect = widgets.FileEdit(mode='d', value=os.path.dirname(sys.path[-1]))

        # GUI integration
        self.viewer.window.add_dock_widget(self.liveGUI, area='right', name='Acquisition parameter')
        self.viewer.window.add_dock_widget(widgets.Container(widgets=[self.dirSelect]), area='right', name='File save directory')
        # pos
        self.viewer.window.add_dock_widget(widgets.Container(widgets=[self.NDSelectionBottom]), area='right', name='Position selection')
        self.viewer.window.add_dock_widget(widgets.Container(widgets=[self.firstPhase, self.secondPhase, self.PhaseNum, self.LoopStep, self.estimateTime]),
                                    area='right', name='ND setup')
        
    def calcEstimateTime(self):
        time = self.LoopStep[0].value * (self.firstPhaseNum.value + self.secondPhaseNum.value) * self.LoopStep[1].value
        self.estimateTime.value = minute2Time(time)

    def update_point(self, index):
        self.viewer.dims.set_point(axis=0, value=index)

    # @thread_worker(connect={'yielded': self.update_point})
    @thread_worker
    def get_image_index(self, ):
        index_0 = self.camera.current_index
        while self.camera.live_flag:
            if self.camera.current_index != index_0:
                index_0 = self.camera.current_index
                time.sleep(1 / 50)  # 50 frame/s is good for all.
                yield self.camera.current_index

    def connect_triggerBottom(self, value):
        if value:
            # 1. check live layer
            layer_names = [la.name for la in self.viewer.layers]
            if 'Live' not in layer_names:
                self.viewer.add_image(self.camera.buffer, name='Live')
            # 2. live camera
            self.camera.live()

            # viewer.dims.set_point(axis=0, value=camera.current_index)
            worker = self.get_image_index()
            worker.yielded.connect(self.update_point)
            worker.start()
            # worker.start()
        else:
            self.camera.live_stop()


    def connect_exposureTime(self, value):
        self.camera.time_step = value
        
    def connect_triggerChoice(self, value):
        pass

    def connect_snapBottom(self, alue):
        pass

    def interconnect_change_guipars(self, value):
        microconfig = self.acq_config.get_config(value)
        self.exposureTime.value = microconfig['exposure']
        self.triggerChoice.value = microconfig['exciterSate']
        self.intensityBar.value = float(list(microconfig['intensity'].values())[0])
        print(microconfig)

    def config_connect_change_exposure(self, value):
        current_setup = self.acqSetUpChoice.value
        microconfig = self.acq_config.get_config(current_setup)
        microconfig['exposure'] = self.exposureTime.value
        # acq_config.load_config(current_setup, microconfig)

    def config_connect_change_exciterSate(self, value):
        current_setup = self.acqSetUpChoice.value
        microconfig = self.acq_config.get_config(current_setup)
        microconfig['exciterSate'] = self.triggerChoice.value
        # acq_config.load_config(current_setup, microconfig)

    def config_connect_change_intensity(self, value):
        current_setup = self.acqSetUpChoice.value
        microconfig = self.acq_config.get_config(current_setup)
        intensity_key = list(microconfig['intensity'].keys())[0]
        microconfig['intensity'][intensity_key] = self.intensityBar.value
        # acq_config.load_config(current_setup, microconfig)


acq_viewer  = AcqViewer()
napari.run()
