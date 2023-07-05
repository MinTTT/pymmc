"""
@author: CHU Pan
@email: pan_chu@outlook.com
"""
import os
import numpy as np
import time
from napari.qt.threading import thread_worker
import tifffile as tif
from tqdm import tqdm

import warnings
import napari
import sys

from typing import Optional
import threading
from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QShortcut, QWidget
from PySide2.QtCore import Qt, QObject
from PySide2.QtGui import QKeySequence
from pymmc_UI.pymmc_ND_pad import Ui_MainWindow
from napari.window import Window
from random import random
from functools import partial
from typing import Optional

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
            
    def get_xy_position(self, ):
        return [random(), random()]
    
    def set_xy_position(self, xy):
        print(f'Go to xy {xy}')
        
    def device_busy(self, ):
        
        time.sleep(.1)
        return False
    
    def open_NDUI(self):
        def open_in_subprocess(obj):
            if not QApplication.instance():
                app = QApplication(sys.argv)
            else:
                app = QApplication.instance()
            ui = NDRecorderUI(obj)
            ui.show()
            app.exec()

        threading.Thread(target=open_in_subprocess, args=(self,)).start()


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
        

class NDRecorderUI(QMainWindow, Ui_MainWindow):
    def __init__(self, acq_obj, test: bool = False):
        """
        Connect UI action to device
        """
        self.acq_obj = acq_obj
        super(NDRecorderUI, self).__init__()
        
        self.setupUi(self)
        if test:
            self.positions = self.acq_obj.positions
            print('Test Mode ON.')
        else:
            self.positions = self.acq_obj.nd_recorder.positions
            print('Loading ND Recorder')
        self.pos_table = self.ND_table
        self.update_button = self.update
        self.right_step.setValue(150)
        self.left_step.setValue(150)
        self.up_step.setValue(150)
        self.down_step.setValue(150)
        self.record_position.clicked.connect(self.do_record_pos)
        self.pos_table.itemClicked.connect(self.row_title_clicked)
        self.update_button.clicked.connect(self.do_update_pos)
        self.selected_index = []
        self.move_up.clicked.connect(partial(self.move_xy, 'up'))
        self.move_down.clicked.connect(partial(self.move_xy, 'down'))
        self.move_right.clicked.connect(partial(self.move_xy, 'right'))
        self.move_left.clicked.connect(partial(self.move_xy, 'left'))
        self.delete_pos.clicked.connect(self.del_pos)


        keydict = dict(right=["Right", partial(self.move_xy, 'right')],
                       left=["Left", partial(self.move_xy, 'left')],
                       up=['Up', partial(self.move_xy, 'up')],
                       down=['Down', partial(self.move_xy, 'down')],
                       record=['Space', self.do_record_pos],
                       update=["U", self.do_update_pos])
        self.bound_shortcut(keydict)

        self.write_table()
        print(f'{self.acq_obj.get_position_dict()}')

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
        
        # @thread_worker
        # def recored_pos(obj):
        #     pos = obj.acq_obj.record_current_position()
        #     print(pos)
        #     obj.edit_row(obj.acq_obj.current_position, pos)
            
        # worker = recored_pos(self)
        # worker.start()
        pos = self.acq_obj.record_current_position()
        print(pos)
        self.edit_row(self.acq_obj.current_position, pos)
        return None


    def do_update_pos(self):
        pos = self.acq_obj.update_current_position()
        self.edit_row(self.acq_obj.current_position, pos)

    def row_title_clicked(self, item):
        row = self.pos_table.currentRow()
        column = self.pos_table.currentColumn()
        if self.checkBox_2.isChecked():
            self.acq_obj.go_to_position(row)

    def move_xy(self, direction: str):
        if direction == 'left':
            self.acq_obj.move_left(dist=float(self.left_step.value()))
        elif direction == 'right':
            self.acq_obj.move_right(dist=float(self.right_step.value()))
        elif direction == 'up':
            self.acq_obj.move_up(dist=float(self.up_step.value()))
        elif direction == 'down':
            self.acq_obj.move_down(dist=float(self.down_step.value()))

    def del_pos(self):
        del_index = [i for i in range(self.pos_table.rowCount()) if
                     self.pos_table.item(i, 4).checkState() == Qt.Checked]

        self.acq_obj.remove_positions(del_index)

        self.pos_table.clear()
        self.write_table()


class Rand_camera:
    def __init__(self, xyz_controller=None, imsize=(2048, 2048), depth=np.uint16):
        self.xyz_controller = xyz_controller
        self._image_size = imsize
        self._depth = depth
        self._flag = None
        self.napari_viewer = None  # type: Optional[napari.Viewer]
        self._img_gen = None
        self.colormap_set = {'green': 'green', 'red': 'red', 'bf': 'gray'}
        self.xyzPanelwindow = None

    def open_viewer(self):
        try:
            if self.napari_viewer is None:
                self.napari_viewer = napari.Viewer()
            # self.napari_viewer.show()
            napari.run()
        except RuntimeError:
            self.napari_viewer = napari.Viewer()
            # self.napari_viewer.run()
            napari.run()
        return None

    def open_xyz_control_panel(self):
        if self.xyz_controller:

            self.open_viewer()
        
            self.xyzPanelwindow = NDRecorderUI(self.xyz_controller, test=False)
            self.xyzPanelwindow.show()
            napari.run()


            
        
        else:
            warnings.warn("XYZ Controller isn't detected.")

    def start_live(self, obj, channel_name):
        @thread_worker(connect={'yielded': self.update_layer})
        def _camera_image(obj, layer_name):
            
            im_count = 0
            if self._flag is None:
                self._flag = True
            try:
                while obj.live_flag:
                    while obj.mmCore.get_remaining_image_count() == 0:
                        time.sleep(0.001)

                    img = obj.mmCore.get_last_image().reshape(obj.img_shape)
                    # obj.img_buff = obj.mmCore.pop_next_image().reshape(obj.img_shape)                    
                    im_count += 1
                    print(im_count)
                    yield (img, layer_name)
            except:
                print('Some happen')
                
            # obj.napari.stop_live()
            # obj.trigger.stop_trigger_continuously()
            # obj.mmCore.stop_sequence_acquisition()
            # obj.stopAcq()
            return None
        
        
        self._flag = True
        if self.napari_viewer is None:
            self.napari_viewer = napari.Viewer()
            
        if not obj.acq_state:
            obj.initAcq()
        print('start live!')
        obj.trigger.trigger_continuously()
        obj.live_flag = True
        _camera_image(obj, channel_name)
            

        # self.camera_live(obj, channel_name)
        return None



    def update_layer(self, args):
        """
        Parameters:
            args: tuple
                (new_image, layerName)
        """
        new_image, layerName = args
        try:
            # if the layer exists, update the data
            self.napari_viewer.layers[layerName].data = new_image
        except KeyError:
            # otherwise add it to the viewer
            try:
                cmap = self.colormap_set[layerName]
            except KeyError:
                cmap = 'gray'
            self.napari_viewer.add_image(new_image,
                                         name=layerName,
                                         blending='additive',
                                         colormap=cmap)
        return None


    
    def stop_live(self):
        self._flag = False    

    def large_random_images(self):
        @thread_worker(connect={'yielded': self.update_layer})
        def _large_random_images():
            if self._flag is None:
                self._flag = True

            random_img = (np.random.random(self._image_size) * 2 ** 16).astype(self._depth)
            while self._flag:
                time.sleep(.01)
                random_img = (np.random.random(self._image_size) * 2 ** 16).astype(self._depth)
                yield random_img
            return random_img

        _large_random_images()

    def update_vedio_layers(self, args):
        """

        :param args: (new_imgs, layerindex, layername)
        :return:
        """
        new_imgs, layerindex, layername = args
        try:
            # if the layer exists, update the data
            self.napari_viewer.layers[layername].data = new_imgs
        except KeyError:
            # otherwise add it to the viewer
            self.napari_viewer.add_image(new_imgs, name=layername)
        self.napari_viewer.dims.set_point(0, layerindex)
        return None

    def update_index_from_AcqTrigger(self, obj):
        @thread_worker(connect={'yielded': self.update_layer})
        def _update_index(obj):
            im_count = 0
            obj.current_index = 0
            pbar = tqdm(total=len(obj.img_buff))  # create progress bar
            while im_count < len(obj.img_buff):
                _time_cur = time.time()
                while obj.mmCore.get_remaining_image_count() == 0:
                    pass
                if obj.mmCore.get_remaining_image_count() > 0:
                    obj.img_buff[im_count, ...] = obj.mmCore.pop_next_image().reshape(obj.img_shape)
                    yield obj.img_buff[im_count, ...], obj.current_channel
                    obj.current_index = im_count
                    im_count += 1
                    pbar.update(1)

            obj.trigger.stop_trigger_continuously()
            obj.stopAcq()
            pbar.close()
            yield obj.img_buff, obj.current_channel
            return None

        _update_index(obj)

        return None

    def update_index(self, args):
        """
        update image index
        :param args: (axis, index)
        :return:
        """
        axis, index = args
        self.napari_viewer.dims.set_point(axis, index)
        return None

    def acq_random_images(self, duration_time, step, im_name, dir):
        frame_num = round(duration_time / step)
        img_buffer = np.empty(shape=(frame_num, *self._image_size)).astype(self._depth)
        self.open_viewer()

        @thread_worker(connect={'yielded': self.update_vedio_layers})
        def _acq_random_images(buffer, name, dir):
            franme_num = buffer.shape[0]
            for i in range(franme_num):
                time.sleep(step)
                random_img = (np.random.random(self._image_size) * 2 ** 16).astype(self._depth)
                buffer[i, ...] = random_img
                yield buffer, i, im_name
            tif.imsave(os.path.join(dir, f'{name}.tiff'), buffer)
            return None

        _acq_random_images(img_buffer, im_name, dir)
        return None


# %%
if __name__ == '__main__':
    camera = Rand_camera()
    for i in range(3):
        imgs = camera.acq_random_images(20, 0.1, f'random vedio{i}', r'./')

# flag = [True]
#
# large_random_images(flag)  # call the function!
# np_viewer


# %%

#
# @thread_worker
# def grab_img(np_viewer:napari.Viewer, flag=None, time_step=.01):
#
#     if flag is None:
#         flag = [True]
#     while flag[0]:
#         time.sleep(time_step)
#         if np_viewer.layers:
#             layer_data = np_viewer.layers[0].data
#             layer = np_viewer.layers[0]
#
#             random_img = (np.random.random(random_img.shape) * 2 ** 8 - 1).astype(np.uint8)
#             random_imgs = np.concatenate((layer_data, random_img), axis=0)
#             layer.data = random_imgs
#         else:
#             random_img = cell()
#             random_img = random_img[np.newaxis, :]
#             np_viewer.add_image(random_img, rendering='attenuated_mip')
#
#         np_viewer.dims.set_point(0, layer.data.shape[0] - 1)
#
# flag = [True]
# # threading.Thread(target=grab_img, args=(np_viewer, flag)).start()

# #%%
# for i in tqdm(range(10)):
#     time.sleep(1)
#     if np_viewer.layers:
#         layer_data = np_viewer.layers[0].data
#         layer = np_viewer.layers[0]
#
#         random_img = (np.random.random(random_img.shape) * 2 ** 8 - 1).astype(np.uint8)
#         random_imgs = np.concatenate((layer_data, random_img), axis=0)
#         layer.data = random_imgs
#     else:
#         random_img = cell()
#         random_img = random_img[np.newaxis, :]
#         np_viewer.add_image(random_img, rendering='attenuated_mip')
#
#     np_viewer.dims.set_point(0, layer.data.shape[0]-1)
