# %%

import time
import pymm_device_light_path_cfg as pymm_cfg
import os
import sys
from pymm_uitls import colors, get_filenameindex, countdown, parse_second, parse_position, NDRecorder, h5_image_saver
from typing import Optional
from PySide6.QtWidgets import QApplication
from pymmc_UI.ND_pad_main_py import NDRecorderUI
import threading as thread
import numpy as np
import tifffile as tiff
from tqdm import tqdm
from functools import partial
from typing import Callable

bcolors = colors()

saving_lock = thread.Lock()
import _thread
import napari
from napari.qt.threading import thread_worker


# studio = mm.studio

def save_tyx(image_ps, image: np.ndarray, ijmeta={}):
    file_type = image_ps.split('.')[-1]
    ijmeta.update({'axes': 'TYX'})
    print(f'[{image_ps}] -> Waiting.')
    saving_lock.acquire()
    print(f'[{image_ps}] -> Writing.')
    if file_type in ['tiff', 'tif']:
        tiff.imwrite(file=image_ps, data=image, imagej=True, metadata=ijmeta)
    elif file_type in ['h5']:
        image_number = len(image)
        ijmeta.update({f'image_data/{i}': image[i, ...] for i in range(image_number)})
        ijmeta.update({f'frame': [f'{i + 1}/{image_number}' for i in range(image_number)]})
        h5_image_saver(image_ps, ijmeta)
    # tiff.imsave(file=image_ps, data=image, imagej=True, metadata={'axes': 'TYX'}.update(ijmeta))
    saving_lock.release()
    print(f'[{image_ps}] -> Success.')
    return None


class PymmAcq:

    def __init__(self, device: str):
        self.device_name = device
        self.stop = [False]
        self.device_cfg = None  # type: pymm_cfg.MicroscopeParas
        self.nd_recorder = NDRecorder()
        self.time_step = None
        self._current_position = None  # type: Optional[int]
        self.initialize_device()
        self.napari_viewer = None

        self.img_depth = None
        self.img_shape = None

        self._live_status = None

    def _get_img_info(self):
        depth_dict = {16: np.uint16, 8: np.uint8, 12: np.uint16}

        width, height = self.device_cfg.mmcore.get_image_width(), self.device_cfg.mmcore.get_image_height()
        self.img_shape = (height, width)
        self.img_depth = depth_dict[self.device_cfg.mmcore.get_image_bit_depth()]

    def _init_camera_acq(self):
        """
        Reset the camera state.
        :return:
        :rtype:
        """
        if self.device_cfg.mmcore.is_sequence_running():
            self.device_cfg.mmcore.stop_sequence_acquisition()
        self.device_cfg.mmcore.clear_circular_buffer()
        self.device_cfg.mmcore.prepare_sequence_acquisition(self.device_cfg.mmcore.get_camera_device())

    def open_viewer(self):
        try:
            if self.napari_viewer is None:
                self.napari_viewer = napari.Viewer()
            self.napari_viewer.show()
        except RuntimeError:
            self.napari_viewer = napari.Viewer()
            self.napari_viewer.show()

    @property
    def current_position(self) -> Optional[int]:
        return self._current_position

    def initialize_device(self):
        self.device_cfg = pymm_cfg.MicroscopeParas(self.device_name)

    def record_current_position(self):
        pos = self.device_cfg.get_position_dict()
        self.nd_recorder.add_position(self.device_cfg.get_position_dict())
        self._current_position = self.nd_recorder.position_number - 1
        return pos

    def update_current_position(self):
        current_pos = self.device_cfg.get_position_dict()
        self.nd_recorder.update_position(self._current_position, self.device_cfg.get_position_dict())
        return current_pos

    def remove_positions(self, pos_index):
        for i in sorted(pos_index, reverse=True):
            del self.nd_recorder.positions[i]

    def move_right(self, dist=127, convert=False):
        pos = self.device_cfg.get_position_dict()
        if convert:
            pos['xy'][0] -= dist
        else:
            pos['xy'][0] += dist
        self.device_cfg.move_xyz_pfs(pos, step=0)

    def move_left(self, dist=127, convert=False):
        pos = self.device_cfg.get_position_dict()
        if convert:
            pos['xy'][0] += dist
        else:
            pos['xy'][0] -= dist
        self.device_cfg.move_xyz_pfs(pos, step=0)

    def move_up(self, dist=127, convert=False):
        pos = self.device_cfg.get_position_dict()
        if convert:
            pos['xy'][1] -= dist
        else:
            pos['xy'][1] += dist
        self.device_cfg.move_xyz_pfs(pos, step=0)

    def move_down(self, dist=127, convert=False):
        pos = self.device_cfg.get_position_dict()
        if convert:
            pos['xy'][1] += dist
        else:
            pos['xy'][1] -= dist
        self.device_cfg.move_xyz_pfs(pos, step=0)

    def go_to_position(self, index):
        pos = self.nd_recorder.positions[index]
        self.device_cfg.move_xyz_pfs(pos, step=0)
        self._current_position = self.nd_recorder.positions.index(pos)

    def go_to_next_position(self):
        if self._current_position + 1 >= self.nd_recorder.position_number:
            print("Here is the last position.")
            return None
        self._current_position += 1
        self.go_to_position(self._current_position)

    def go_to_previous_position(self):
        if self._current_position <= 0:
            print("Here is the first position.")
            return None
        self._current_position -= 1
        self.go_to_position(self._current_position)

    def multi_acq_3c(self, dir: str, pos_ps: str = None, time_step: list = None, flu_step: int = None,
                     time_duration: list = None):
        _thread.start_new_thread(multi_acq_3c,
                                 (dir, pos_ps, self, time_step, flu_step, time_duration, self.stop))
        return None

    def multi_acq_3c_sync_light(self, dir: str, pos_ps: str = None, time_step: list = None, flu_step: int = None,
                                time_duration: list = None):
        thread.Thread(target=multi_acq_3c_sync_light,
                      args=(dir, pos_ps, self, time_step, flu_step, time_duration, self.stop)).start()
        # _thread.start_new_thread(multi_acq_3c_sync_light, (dir, pos_ps, self, time_step, flu_step, time_duration, self.stop))
        return None

    def multi_acq_4c(self, dir: str, pos_ps: str, time_step: list, flu_step: int, time_duration: list):
        _thread.start_new_thread(multi_acq_4c,
                                 (dir, pos_ps, self.device_cfg, time_step, flu_step, time_duration, self.stop))
        return None

    def multi_acq_2c(self, dir: str, pos_ps: str = None, time_step: list = None, flu_step: int = None,
                     time_duration: list = None):
        # _thread.start_new_thread(multi_acq_2c,
        #                         (dir, pos_ps, self, time_step, flu_step, time_duration, self.stop))
        thread.Thread(target=multi_acq_2c,
                      args=(dir, pos_ps, self, time_step, flu_step, time_duration, self.stop)).start()
        return None

    def stop_acq_loop(self):
        self.stop[0] = True
        return None

    def open_NDUI(self):
        def open_in_subprocess(obj):
            if not QApplication.instance():
                app = QApplication(sys.argv)
            else:
                app = QApplication.instance()
            ui = NDRecorderUI(obj)
            ui.show()
            app.exec()

        thread.Thread(target=open_in_subprocess, args=(self,)).start()

    def sequence_acq(self, duration_time: float, step: float, exposure: float = None, save_dir: str = None):
        """

        :param duration_time: duration time, how long will acquisition lasting. unit: ms
        :param step: time interval. unit: ms
        :param exposure: exposure time. unit: ms
        :param save_dir: sequence images save dir. if None, return numpy array (t, y, x)
        :return: None or ndarray
        """

        self._get_img_info()

        if exposure is not None:
            self.device_cfg.mmcore.set_exposure(exposure)
        frame_num = round(duration_time / step)

        # create a video buffer
        vedio = np.empty((frame_num, *self.img_shape), dtype=self.img_depth)
        self._init_camera_acq()

        print('start acq!')
        self.device_cfg.mmcore.start_sequence_acquisition(frame_num, step, False)
        for i in tqdm(range(frame_num)):
            while self.device_cfg.mmcore.get_remaining_image_count() == 0:
                time.sleep(0.0005)
            if self.device_cfg.mmcore.get_remaining_image_count() > 0:
                vedio[i] = self.device_cfg.mmcore.pop_next_image().reshape(*self.img_shape)
        self.device_cfg.mmcore.stop_sequence_acquisition()

        if save_dir is None:
            return vedio
        else:
            _ = _thread.start_new_thread(save_tyx, (save_dir, vedio,))
            return None

    def update_napari_layer(self, new_image):
        try:
            # if the layer exists, update the data
            self.napari_viewer.layers['Live Camera'].data = new_image
        except KeyError:
            # otherwise add it to the viewer
            self.napari_viewer.add_image(new_image, name='Live Camera')

    def stream_acq(self, step):
        @thread_worker(connect={"yielded": self.update_napari_layer})
        def _stream_acq(step: float):
            self.device_cfg.mmcore.start_continuous_sequence_acquisition(float(step))
            img = np.zeros(self.img_shape).astype(self.img_depth)

            while self._live_status:

                while self.device_cfg.mmcore.get_remaining_image_count() == 0:
                    pass
                if self.device_cfg.mmcore.get_remaining_image_count() > 0:
                    img = self.device_cfg.mmcore.pop_next_image().reshape(*self.img_shape)
                    yield img

            self.device_cfg.mmcore.stop_sequence_acquisition()
            return img

        _stream_acq(step)

    def start_streaming(self, step):
        """

        :param step:
        :type step:
        :return:
        :rtype:
        """
        self.open_viewer()
        self._live_status = True
        self.stream_acq(step)

    def stop_streaming(self):
        """
        Stop the Live Camera streaming.
        :return:
        :rtype:
        """
        self._live_status = False
        self.device_cfg.mmcore.stop_sequence_acquisition()
        self.device_cfg.mmcore.clear_circular_buffer()

    def continuous_acq(self, duration_time: float, step: float, save_dir: str = None):
        """
        :param duration_time: duration time, how long will acquisition lasting. unit: ms
        :param step: time interval. unit: ms
        :param save_dir: sequence images save dir. if None, return numpy array (t, y, x)
        :return: None or ndarray
        """
        self._get_img_info()

        frame_num = int(duration_time / step)
        self.device_cfg.mmcore.set_exposure(step)
        self.device_cfg.mmcore.set_property(self.device_cfg.mmcore.get_camera_device(), 'Exposure',
                                            step)

        # create a buffer
        vedio = np.empty((round(frame_num*1.01), *self.img_shape), dtype=self.img_depth)
        # if self.device_cfg.mmcore.is_sequence_running():
        #     self.device_cfg.mmcore.stop_sequence_acquisition()
        self._init_camera_acq()

        print('start acq!')
        self.device_cfg.mmcore.start_continuous_sequence_acquisition(float(step))


        im_count = 0
        time_current = time.time()
        pbar = tqdm(total=frame_num)  # create progress bar
        while (time.time() - time_current) * 1000 < duration_time:
            _time_cur = time.time()
            while self.device_cfg.mmcore.get_remaining_image_count() == 0:
                pass
            if self.device_cfg.mmcore.get_remaining_image_count() > 0:
                vedio[im_count] = self.device_cfg.mmcore.pop_next_image().reshape(*self.img_shape)
                im_count += 1
                pbar.update(1)

        self.device_cfg.mmcore.stop_sequence_acquisition()
        while self.device_cfg.mmcore.get_remaining_image_count() != 0:
            vedio[im_count] = self.device_cfg.mmcore.pop_next_image().reshape(*self.img_shape)
            im_count += 1
            pbar.update(1)
        pbar.close()
        vedio = vedio[:im_count, ...]  # clean the buffer
        # frame_rate = self.device_cfg.mmcore.get_property(self.device_cfg.mmcore.get_camera_device(),
        #                                                  'Exposure')
        # print(f'Frame Rate: {frame_rate}')
        print(f'FPS: {im_count / duration_time * 1000}')

        if save_dir is None:
            return vedio
        else:
            save_thread = thread.Thread(target=save_tyx,
                                        args=(save_dir, vedio,
                                              {'frame_rate': f'{im_count / duration_time * 1000}',
                                               'location': f'{self.current_position}'}))
            save_thread.start()
            return None


def get_exposure(state, device_cfg) -> float:
    if state == 'green':
        return device_cfg.EXPOSURE_GREEN
    else:
        return device_cfg.EXPOSURE_RED


def if_acq(loop_index, flu_step):
    try:
        reamin = loop_index % flu_step
        return reamin
    except ZeroDivisionError:
        return 1


def multi_acq_3c(dir: str, pos_ps: str, device: PymmAcq, flu_step: int,
                 time_duration: list,
                 thread_flag=False) -> None:
    '''
    :param dir: image save dir, str
    :param pos_ps: position file, str
    :param device: device cfg, obj
    :param time_step: list [h, min, s]
    :param flu_step: int
    :param time_duration: list [h, min, s]
    :param thread_flag: list
    :return: None
    '''
    DIR = dir
    POSITION_FILE = pos_ps
    # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ
    # -----------------------------------------------------------------------------------
    device_cfg = device.device_cfg
    # %%
    # ==========get multiple positions============
    if POSITION_FILE is not None:
        fovs = parse_position(POSITION_FILE,
                              device=[device_cfg.XY_DEVICE, device_cfg.Z_DEVICE, device_cfg.AUTOFOCUS_OFFSET])
        device.nd_recorder.positions = fovs
    fovs = device.nd_recorder.positions

    # ==========set loop parameters===============
    time_step = device.time_step  # [hr, min, s]
    flu_step = flu_step  # very 4 phase loops acq
    time_duration = time_duration
    loops_num = parse_second(time_duration) // parse_second(time_step)
    print(
        f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

    # %% loop body
    EXPOSURE_PHASE = device_cfg.EXPOSURE_PHASE
    set_device_state = device_cfg.set_device_state
    print(f'{colors.OKGREEN}Initial Device Setup.{colors.ENDC}')
    # device_cfg.set_light_path('BF', '100X')
    light_path_state = 'green'
    set_device_state(device_cfg.mmcore, 'init_phase')
    set_device_state(device_cfg.mmcore, 'r2g')
    time.sleep(2.5)
    # TODO：I found the python console initialized and performed this code block first time,
    #  the Ti2E_H has no fluorescent emission light.
    print(f'{colors.OKGREEN}Start ACQ Loop.{colors.ENDC}')
    loop_index = 0  # default is 0
    while loop_index != loops_num:
        t_init = time.time()
        if if_acq(loop_index, flu_step) == 0:
            for fov_index, fov in enumerate(fovs):
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                device_cfg.move_xyz_pfs(fov, step=6)  # move stage xy.
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                time.sleep(0.5)
                # First Channel
                if light_path_state == 'green':
                    print('Snap image (phase).\n')
                    device_cfg.check_auto_focus(0.5)  # check auto focus, is important!
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    print('Snap image (green).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=get_exposure(light_path_state, device_cfg))
                else:
                    print('Snap image (red).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    device_cfg.check_auto_focus(0.2)
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=get_exposure(light_path_state, device_cfg))
                # Second Channel
                if light_path_state == 'green':
                    light_path_state = 'red'
                    set_device_state(device_cfg.mmcore, 'g2r')
                    device_cfg.check_auto_focus(0.5)  # check auto focus, is important!
                    time.sleep(0.2)
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=get_exposure(light_path_state, device_cfg))
                    print(f'Snap image (red).\n')
                else:
                    light_path_state = 'green'
                    set_device_state(device_cfg.mmcore, 'r2g')
                    device_cfg.check_auto_focus(0.5)  # check auto focus, is important!
                    time.sleep(0.2)  # 1.5 is ok
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    print('Snap image (green).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=get_exposure(light_path_state, device_cfg))
        else:
            # ========start phase 100X acq loop=================#
            if light_path_state == 'green':
                pass
            else:
                light_path_state = 'green'
                set_device_state(device_cfg.mmcore, 'r2g')
                device_cfg.check_auto_focus(0.5)  # check auto focus, is important!

            device_cfg.active_auto_shutter(device_cfg.SHUTTER_LAMP)
            for fov_index, fov in enumerate(fovs):
                device_cfg.move_xyz_pfs(fov, step=6)
                device_cfg.check_auto_focus(0.5)  # check auto focus, is important!
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                print('Snap image (phase).\n')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                device_cfg.auto_acq_save(image_dir, name=file_name,
                                         exposure=EXPOSURE_PHASE)

        # ======================waiting cycle=========

        t_of_acq = time.time() - t_init
        waiting_t = parse_second(time_step) - t_of_acq

        if thread_flag[0] != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None

        if waiting_t < 0:
            print(f'{bcolors.WARNING}Waring: Acquisition loop {t_of_acq} s '
                  f' is longer than default time step ({-int(waiting_t)} s)! '
                  f' and the the next step will start immediately.{bcolors.ENDC}')
        else:
            print(f'Waiting next loop[{loop_index + 1}].')
            countdown(waiting_t, 1, thread_flag)
        if thread_flag[0] != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None
        loop_index += 1
        # ======================waiting cycle=========

    print('finished all loops!')
    return None


def multi_acq_3c_sync_light(dir: str, pos_ps: str, device: PymmAcq, time_step: list, flu_step: int,
                            time_duration: list,
                            thread_flag=False) -> None:
    '''
    :param dir: image save dir, str
    :param pos_ps: position file, str
    :param device: device cfg, obj
    :param time_step: list [h, min, s]
    :param flu_step: int
    :param time_duration: list [h, min, s]
    :param thread_flag: list
    :return: None
    '''
    DIR = dir
    POSITION_FILE = pos_ps
    # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ
    # -----------------------------------------------------------------------------------
    device_cfg = device.device_cfg
    camera_trigger = device_cfg.fpga_core.trigger_one_pulse  # type: Callable
    # %%
    # ==========get multiple positions============
    if POSITION_FILE is not None:
        fovs = parse_position(POSITION_FILE,
                              device=[device_cfg.XY_DEVICE, device_cfg.Z_DEVICE, device_cfg.AUTOFOCUS_OFFSET])
        device.nd_recorder.positions = fovs
    fovs = device.nd_recorder.positions

    # ==========set loop parameters===============
    # time_step  # [hr, min, s]
    # flu_step = flu_step  # very 4 phase loops acq
    # time_duration = time_duration
    loops_num = parse_second(time_duration) // parse_second(time_step)
    print(
        f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

    # %% loop body
    EXPOSURE_PHASE = device_cfg.EXPOSURE_PHASE
    set_device_state = device_cfg.set_device_state
    print(f'{colors.OKGREEN}Initial Device Setup.{colors.ENDC}')
    # device_cfg.set_light_path('BF', '100X')
    light_path_state = 'green'
    set_device_state(device_cfg.mmcore, 'init_phase')
    set_device_state(device_cfg.mmcore, 'r2g')
    device_cfg.image_grabber.init_process()
    time.sleep(1.0)
    # TODO：I found the python console initialized and performed this code block first time,
    #  the Ti2E_H has no fluorescent emission light.
    print(f'{colors.OKGREEN}Start ACQ Loop.{colors.ENDC}')
    loop_index = 0  # default is 0
    while loop_index != loops_num:
        t_init = time.time()
        if if_acq(loop_index, flu_step) == 0:
            for fov_index, fov in enumerate(fovs):
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'  # generate growth rate
                device_cfg.move_xyz_pfs(fov, step=6)  # move stage xy.
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                time.sleep(0.1)
                # First Channel
                if light_path_state == 'green':
                    print('Snap image (phase).\n')
                    device_cfg.check_auto_focus(0.1)  # check auto focus, is important!
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    set_device_state(device_cfg.mmcore, 'phase')
                    device_cfg.auto_acq_save(image_dir, name=file_name, exposure=EXPOSURE_PHASE,
                                             shutter=camera_trigger)
                    print('Snap image (green).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    set_device_state(device_cfg.mmcore, 'fluorescent')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             exposure=get_exposure(light_path_state, device_cfg),
                                             shutter=camera_trigger)
                else:
                    print('Snap image (red).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    device_cfg.check_auto_focus(0.1)
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             exposure=get_exposure(light_path_state, device_cfg),
                                             shutter=camera_trigger)
                # Second Channel
                if light_path_state == 'green':
                    light_path_state = 'red'
                    set_device_state(device_cfg.mmcore, 'g2r')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    device_cfg.check_auto_focus(0.1)  # check auto focus, is important!
                    time.sleep(0.1)
                    print(f'Snap image (red).\n')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             exposure=get_exposure(light_path_state, device_cfg),
                                             shutter=camera_trigger)

                else:
                    light_path_state = 'green'
                    set_device_state(device_cfg.mmcore, 'r2g')
                    device_cfg.check_auto_focus(0.1)  # check auto focus, is important!
                    time.sleep(0.1)  # 1.5 is ok
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    set_device_state(device_cfg.mmcore, 'phase')
                    device_cfg.auto_acq_save(image_dir, name=file_name, exposure=EXPOSURE_PHASE,
                                             shutter=camera_trigger)
                    print('Snap image (green).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                    set_device_state(device_cfg.mmcore, 'fluorescent')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             exposure=get_exposure(light_path_state, device_cfg),
                                             shutter=camera_trigger)
        else:
            # ========start phase 100X acq loop=================#
            if light_path_state == 'green':
                pass
            else:
                light_path_state = 'green'
                set_device_state(device_cfg.mmcore, 'r2g')
                set_device_state(device_cfg.mmcore, 'phase')
                device_cfg.check_auto_focus(0.1)  # check auto focus, is important!

            set_device_state(device_cfg.mmcore, 'phase')
            for fov_index, fov in enumerate(fovs):
                device_cfg.move_xyz_pfs(fov, step=6)
                device_cfg.check_auto_focus(0.1)  # check auto focus, is important!
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                print('Snap image (phase).\n')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                device_cfg.auto_acq_save(image_dir, name=file_name,
                                         exposure=EXPOSURE_PHASE,
                                         shutter=camera_trigger)
        # ======================waiting cycle=========

        t_of_acq = time.time() - t_init
        waiting_t = parse_second(time_step) - t_of_acq

        if thread_flag != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None

        if waiting_t < 0:
            print(f'{bcolors.WARNING}Waring: Acquisition loop {t_of_acq} s '
                  f' is longer than default time step ({-int(waiting_t)} s)! '
                  f' and the the next step will start immediately.{bcolors.ENDC}')
        else:
            print(f'Waiting next loop[{loop_index + 1}].')
            countdown(waiting_t, 1, thread_flag)
        if thread_flag != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None
        loop_index += 1
        # ======================waiting cycle=========
    device_cfg.mmcore.stop_sequence_acquisition(device_cfg.mmcore.get_camera_device())

    print('finished all loops!')
    return None


def multi_acq_4c(dir: str, pos_ps: str, device: object, time_step: list, flu_step: int, time_duration: list,
                 thread_flag=False) -> None:
    '''
    :param dir: image save dir, str
    :param pos_ps: position file, str
    :param device: device cfg, object
    :param time_step: list [h, min, s]
    :param flu_step: int
    :param time_duration: list [h, min, s]
    :param thread_flag: list
    :return: None
    '''
    DIR = dir
    POSITION_FILE = pos_ps
    # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ
    # -----------------------------------------------------------------------------------
    device_cfg = device
    # %%
    # ==========get multiple positions============
    fovs = parse_position(POSITION_FILE,
                          device=[device_cfg.XY_DEVICE, device_cfg.Z_DEVICE, device_cfg.AUTOFOCUS_OFFSET])
    # ==========set loop parameters===============
    time_step = time_step  # [hr, min, s]
    flu_step = flu_step  # very 4 phase loops acq
    time_duration = time_duration
    loops_num = parse_second(time_duration) // parse_second(time_step)
    print(
        f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

    # %% loop body

    EXPOSURE_PHASE = device_cfg.EXPOSURE_PHASE
    set_device_state = device_cfg.set_device_state
    print(f'{colors.OKGREEN}Initial Device Setup.{colors.ENDC}')
    # device_cfg.set_light_path('BF', '100X', shutter=device_cfg.SHUTTER_LAMP)
    light_path_state = 'green'
    print(f'{colors.OKGREEN}Initial Phase Setup.{colors.ENDC}')
    set_device_state(device_cfg.mmcore, 'init_phase')
    print(f'{colors.OKGREEN}Initial First Channel.{colors.ENDC}')
    set_device_state(device_cfg.mmcore, '3t1')
    # TODO：I found the python console initialized and performed this code block first time,
    #  the Ti2E_H has no fluorescent emission light.
    print(f'{colors.OKGREEN}Start ACQ Loop.{colors.ENDC}')
    loop_index = 0  # default is 0
    while loop_index != loops_num:
        t_init = time.time()
        if if_acq(loop_index, flu_step) == 0:
            for fov_index, fov in enumerate(fovs):
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                device_cfg.move_xyz_pfs(fov, step=6, XY_DEVICE=device_cfg.XY_DEVICE)  # move stage xy.
                device_cfg.check_auto_focus()  # check auto focus, is important!
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                # First Channel
                if light_path_state == 'green':
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    print('Snap image (CFP).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'CFP')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_BLUE)
                    set_device_state(device_cfg.mmcore, '1t2')
                    print('Snap image (YFP).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'YFP')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_YELLOW)
                    set_device_state(device_cfg.mmcore, '2t3')
                    print('Snap image (RED).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'RED')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_RED)
                    light_path_state = 'red'
                else:
                    print('Snap image (RED).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'RED')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_RED)
                    set_device_state(device_cfg.mmcore, '3t2')
                    print('Snap image (YFP).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'YFP')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_YELLOW)
                    set_device_state(device_cfg.mmcore, '2t1')
                    print('Snap image (CFP).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'CFP')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LED,
                                             exposure=device_cfg.EXPOSURE_BLUE)
                    print('Snap image (phase).\n')
                    image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                    device_cfg.auto_acq_save(image_dir, name=file_name,
                                             shutter=device_cfg.SHUTTER_LAMP, exposure=EXPOSURE_PHASE)
                    light_path_state = 'green'


        else:
            # ========start phase 100X acq loop=================#
            if light_path_state == 'green':
                pass
            else:
                set_device_state(device_cfg.mmcore, '3t1')
                light_path_state = 'green'
            device_cfg.active_auto_shutter(device_cfg.SHUTTER_LAMP)
            for fov_index, fov in enumerate(fovs):
                device_cfg.move_xyz_pfs(fov, step=6, XY_DEVICE=device_cfg.XY_DEVICE)
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                print('Snap image (phase).\n')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                device_cfg.auto_acq_save(image_dir, name=file_name,
                                         exposure=EXPOSURE_PHASE)

        # ======================waiting cycle=========

        t_of_acq = time.time() - t_init
        waiting_t = parse_second(time_step) - t_of_acq

        if thread_flag != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None

        if waiting_t < 0:
            print(f'{bcolors.WARNING}Waring: Acquisition loop {t_of_acq} s '
                  f' is longer than default time step ({-int(waiting_t)} s)! '
                  f' and the the next step will start immediately.{bcolors.ENDC}')
        else:
            print(f'Waiting next loop[{loop_index + 1}].')
            countdown(waiting_t, 1)
        if thread_flag != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None
        loop_index += 1
        # ======================waiting cycle=========

    print('finished all loops!')
    return None


def multi_acq_2c(dir: str, pos_ps: str, device: PymmAcq, time_step: list, flu_step: int,
                 time_duration: list,
                 thread_flag=False) -> None:
    '''
    :param dir: image save dir, str
    :param pos_ps: position file, str
    :param device: device cfg, obj
    :param time_step: list [h, min, s]
    :param flu_step: int
    :param time_duration: list [h, min, s]
    :param thread_flag: list
    :return: None
    '''
    DIR = dir
    POSITION_FILE = pos_ps
    # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ
    # -----------------------------------------------------------------------------------
    device_cfg = device.device_cfg
    camera_trigger = device_cfg.fpga_core.trigger_one_pulse  # type: Callable
    # %%
    # ==========get multiple positions============
    if POSITION_FILE is not None:
        fovs = parse_position(POSITION_FILE,
                              device=[device_cfg.XY_DEVICE, device_cfg.Z_DEVICE, device_cfg.AUTOFOCUS_OFFSET])
        device.nd_recorder.positions = fovs
    fovs = device.nd_recorder.positions

    # ==========set loop parameters===============
    time_step = time_step  # [hr, min, s]
    flu_step = flu_step  # very 4 phase loops acq
    time_duration = time_duration
    loops_num = parse_second(time_duration) // parse_second(time_step)
    print(
        f'''{loops_num} loops will be performed! Lasting {time_duration[0]} hours/hour and {time_duration[0]} min. \n''')

    # %% loop body
    EXPOSURE_PHASE = device_cfg.EXPOSURE_PHASE
    EXPOSURE_YELLOW = device_cfg.EXPOSURE_YELLOW
    set_device_state = device_cfg.set_device_state
    print(f'{colors.OKGREEN}Initial Device Setup.{colors.ENDC}')
    # device_cfg.set_light_path('BF', '100X')
    light_path_state = 'yellow'
    set_device_state(device_cfg.mmcore, 'init_phase')
    device_cfg.image_grabber.init_process()
    time.sleep(2.5)
    # TODO：I found the python console initialized and performed this code block first time,
    #  the Ti2E_H has no fluorescent emission light.
    print(f'{colors.OKGREEN}Start ACQ Loop.{colors.ENDC}')
    loop_index = 0  # default is 0
    while loop_index != loops_num:
        t_init = time.time()
        if if_acq(loop_index, flu_step) == 0:
            for fov_index, fov in enumerate(fovs):
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                device_cfg.move_xyz_pfs(fov, step=6)  # move stage xy.
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                # time.sleep(0.5)
                # First Channel
                print('Snap image (yellow).\n')
                set_device_state(device_cfg.mmcore, 'fluorescent')
                image_dir = os.path.join(DIR, f'fov_{fov_index}', light_path_state)
                device_cfg.auto_acq_save(image_dir, name=file_name,
                                         shutter=camera_trigger,
                                         exposure=EXPOSURE_YELLOW)

                print('Snap image (phase).\n')
                set_device_state(device_cfg.mmcore, 'phase')
                device_cfg.check_auto_focus(0.1)  # check auto focus, is important!
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                device_cfg.auto_acq_save(image_dir, name=file_name,
                                         shutter=camera_trigger, exposure=EXPOSURE_PHASE)

        else:
            # ========start phase 100X acq loop=================#
            device_cfg.check_auto_focus(0.1)  # check auto focus, is important!

            device_cfg.active_auto_shutter(device_cfg.SHUTTER_LAMP)
            for fov_index, fov in enumerate(fovs):
                device_cfg.move_xyz_pfs(fov, step=6)
                device_cfg.check_auto_focus(0.1)  # check auto focus, is important!
                image_dir = os.path.join(DIR, f'fov_{fov_index}', 'phase')
                set_device_state(device_cfg.mmcore, 'phase')
                file_name = f't{get_filenameindex(image_dir)}'
                print(f'''go to next xy[{fov_index + 1}/{len(fovs)}].\n''')
                print('Snap image (phase).\n')
                device_cfg.auto_acq_save(image_dir, name=file_name,
                                         exposure=EXPOSURE_PHASE,
                                         shutter=camera_trigger)

        # ======================waiting cycle=========

        t_of_acq = time.time() - t_init
        waiting_t = parse_second(time_step) - t_of_acq

        if thread_flag != False:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None

        if waiting_t < 0:
            print(f'{bcolors.WARNING}Waring: Acquisition loop {t_of_acq} s '
                  f' is longer than default time step ({-int(waiting_t)} s)! '
                  f' and the the next step will start immediately.{bcolors.ENDC}')
        else:
            print(f'Waiting next loop[{loop_index + 1}].')
            countdown(waiting_t, 1, thread_flag)
        if thread_flag:
            if thread_flag[0]:
                print('Acquisition loop finish!')
                thread_flag[0] = False
                return None
        loop_index += 1
        # ======================waiting cycle=========

    print('finished all loops!')
    return None
