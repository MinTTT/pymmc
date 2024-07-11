"""
magicgui with threadworker
==========================

An example of calling a threaded function from a magicgui ``dock_widget``.
Note: this example requires python >=m 3.9

.. tags:: gui
"""

#%%
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


camera = randCamera(100, 512, 512)
#%%

# viewer = napari.Viewer()
# # GUI 1. live view
# def update_point(index):
#     viewer.dims.set_point(axis=0, value=index)


# @thread_worker(connect={'yielded': update_point})
# def get_image_index():
#     index_0 = camera.current_index
#     while camera.live_flag:
#         if camera.current_index != index_0:
#             index_0 = camera.current_index
#             time.sleep(1 / 100)
#             yield camera.current_index


# def connect_triggerBottom(value):
#     if value:
#         # 1. check live layer
#         layer_names = [la.name for la in viewer.layers]
#         if 'Live' not in layer_names:
#             viewer.add_image(camera.buffer, name='Live')
#         # 2. live camera
#         camera.live()
#         # viewer.dims.set_point(axis=0, value=camera.current_index)
#         get_image_index()
#         # worker.start()
#     else:
#         camera.live_stop()

#     # print(value)


# def connect_exposureTime(value):
#     camera.time_step = value
    


# def connect_triggerChoice(value):
#     pass


# def connect_snapBottom(value):
#     pass


# def interconnect_change_guipars(value):

#     microconfig = acq_config.get_config(value)
    
#     exposureTime.value = microconfig['exposure']
#     triggerChoice.value = microconfig['exciterSate']
#     intensityBar.value = float(list(microconfig['intensity'].values())[0])
#     print(microconfig)

# def config_connect_change_exposure(value):
#     current_setup = acqSetUpChoice.value
#     microconfig = acq_config.get_config(current_setup)
#     microconfig['exposure'] = exposureTime.value
#     # acq_config.load_config(current_setup, microconfig)

# def config_connect_change_exciterSate(value):
#     current_setup = acqSetUpChoice.value
#     microconfig = acq_config.get_config(current_setup)
#     microconfig['exciterSate'] = triggerChoice.value
#     # acq_config.load_config(current_setup, microconfig)

# def config_connect_change_intensity(value):
#     current_setup = acqSetUpChoice.value
#     microconfig = acq_config.get_config(current_setup)
#     intensity_key = list(microconfig['intensity'].keys())[0]
#     microconfig['intensity'][intensity_key] = intensityBar.value
#     # acq_config.load_config(current_setup, microconfig)

# triggerMap = {'phase': 0b01000000,
#               'none': 0b00000000,
#               'red': 0b00000001,
#               'green': 0b00000010,
#               'cyan': 0b00000100,
#               'teal': 0b00001000,
#               'blue': 0b00010000,
#               'violet': 0b00100000}

# acq_setup = {'bf': {'exciterSate': 'phase', 'exposure': 25, 'intensity': {'Intensity': 24}},
#              'green': {'exciterSate': 'cyan', 'exposure': 20, 'intensity': {'Cyan_Level': 20}},
#              'red': {'exciterSate': 'green', 'exposure': 100, 'intensity': {'Green_Level': 50}}}

# acq_config = microConfigManag(config_dict=acq_setup)


# triggerChoiceList = list(triggerMap.keys())
# acqSetUpChoice = widgets.Combobox(value=acq_config.config_names[1], choices=acq_config.config_names, 
#                                   label='Acquisition Setup')
# exposure_Time = dict(value=20., min=15., max=1000., step=1.)  # value, min, max, step
# intensityBar = widgets.FloatSlider(value=0., min=0., max=100., step=1, label='Intensity: ')
# startBottom = widgets.ToggleButton(text='Start/Stop Live', value=False)
# snapBottom = widgets.PushButton(text='Snap', value=False)
# triggerChoice = widgets.ComboBox(value=triggerChoiceList[0],
#                                  choices=triggerChoiceList, label='Trigger type: ')
# exposureTime = widgets.FloatSpinBox(**exposure_Time, label='Exposure time (ms): ')
# configParsWidges = widgets.Container(widgets=[triggerChoice, exposureTime, intensityBar])
# liveGUI = widgets.Container(widgets=[acqSetUpChoice, configParsWidges,
#                                      widgets.Container(widgets=[startBottom, snapBottom], layout='horizontal')])

# interconnect_change_guipars(acq_config.config_names[1])  # init all Acq parameters
# acqSetUpChoice.changed.connect(interconnect_change_guipars)
# startBottom.changed.connect(connect_triggerBottom)
# snapBottom.changed.connect(connect_snapBottom)
# triggerChoice.changed.connect(config_connect_change_exciterSate)
# exposureTime.changed.connect(config_connect_change_exposure)
# intensityBar.changed.connect(config_connect_change_intensity)

# # GUI 2. ND acq

# def minute2Time(minute: float):
#     return '%i:%i:%.1f' % (minute // 60, minute % 60 // 1, minute % 60 % 1 * 60)

# def calcEstimateTime():
#     time = LoopStep[0].value * (firstPhaseNum.value + secondPhaseNum.value) * LoopStep[1].value
#     estimateTime.value = minute2Time(time)


# firstPhase = widgets.Container(widgets=[widgets.CheckBox(value=False, text=key) for key in acq_setup.keys()],
#                                label='1st phase', layout='horizontal')
# secondPhase = widgets.Container(widgets=[widgets.CheckBox(value=False, text=key) for key in acq_setup.keys()],
#                                 label='2nd phase', layout='horizontal')
# firstPhaseNum = widgets.FloatSpinBox(value=1, min=1, step=1, label='1st phase number/loop: ')
# secondPhaseNum = widgets.FloatSpinBox(value=0, min=0, step=1, label='2nd phase number/loop: ')
# PhaseNum = widgets.Container(widgets=[firstPhaseNum, secondPhaseNum])
# LoopStep = widgets.Container(widgets=[widgets.FloatSpinBox(value=1, min=0, step=.1, label='Loop time Step (min): '),
#                                       widgets.FloatSpinBox(value=1, min=1, step=1, label='Loop number: ')])

# estimateTime = widgets.Label(label='Estimate time: ')
# calcEstimateTime()

# LoopStep.changed.connect(calcEstimateTime)
# PhaseNum.changed.connect(calcEstimateTime)
# PhaseNum.changed.connect(calcEstimateTime)

# # GUI 3. ND pad
# # acq_loop = FakeAcq()
# # NDSelectionUI = NDRecorderUI(acq_loop, test=True)
# # def show_NDSelectionUI():
# #     acq_loop.open_NDUI(test_flag=True)

# NDSelectionBottom = widgets.PushButton(text='Open location selection', value=False)
# # NDSelectionBottom.changed.connect(show_NDSelectionUI)

# # GUI 3. save direct
# dirSelect = widgets.FileEdit(mode='d', value=os.path.dirname(sys.path[-1]))

# # GUI integration
# viewer.window.add_dock_widget(liveGUI,
#                               area='right', name='Acquisition parameter')
# viewer.window.add_dock_widget(widgets.Container(widgets=[dirSelect]),
#                               area='right', name='File save directory')
# # pos
# viewer.window.add_dock_widget(widgets.Container(widgets=[NDSelectionBottom]),
#                               area='right', name='Position selection')
# viewer.window.add_dock_widget(widgets.Container(widgets=[firstPhase, secondPhase, PhaseNum, LoopStep, estimateTime]),
#                               area='right', name='ND setup')



# napari.run()





# %%
import Acq_parameters as acq_paras

class AcqViewer:
    
    def __init__(self) -> None:
        self.viewer = napari.Viewer()
        self.camera = randCamera(100, 512, 512)  # wrapper for provide images and controlling image acq
        self.triggerMap = acq_paras.trigger_map

        self.acq_setup = acq_paras.channels

        self.acq_config = microConfigManag(config_dict=self.acq_setup)
        
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

        # GUI 3. save direct
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

# %%

