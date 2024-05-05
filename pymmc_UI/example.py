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

# from ND_pad_main_py import FakeAcq
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
    buffer: Optional[np.ndarray] = None

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
viewer = napari.Viewer()


# GUI 1. live view
def update_point(index):
    viewer.dims.set_point(axis=0, value=index)


@thread_worker(connect={'yielded': update_point})
def get_image_index():
    index_0 = camera.current_index
    while camera.live_flag:
        if camera.current_index != index_0:
            index_0 = camera.current_index
            time.sleep(1 / 100)
            yield camera.current_index


def connect_triggerBottom(value):
    if value:
        # 1. check live layer
        layer_names = [la.name for la in viewer.layers]
        if 'Live' not in layer_names:
            viewer.add_image(camera.buffer, name='Live')
        # 2. live camera
        camera.live()
        # viewer.dims.set_point(axis=0, value=camera.current_index)
        get_image_index()
        # worker.start()
    else:
        camera.live_stop()

    print(value)


def connect_exposureTime(value):
    camera.time_step = value
    print(value)


def connect_triggerChoice(value):
    print(value)


def connect_snapBottom(value):
    print(value)


triggerMap = {'phase': 0b01000000,
              'none': 0b00000000,
              'red': 0b00000001,
              'green': 0b00000010,
              'cyan': 0b00000100,
              'teal': 0b00001000,
              'blue': 0b00010000,
              'violet': 0b00100000}

acq_setup = {'bf': {'exciterSate': 'phase', 'exposure': 25, 'intensity': {'Intensity': 24}},
             'green': {'exciterSate': 'cyan', 'exposure': 20, 'intensity': {'Cyan_Level': 20}},
             'red': {'exciterSate': 'green', 'exposure': 100, 'intensity': {'Green_Level': 50}}}

acq_config = microConfigManag(config_dict=acq_setup)

triggerChoiceList = list(triggerMap.keys())
acqSetUpChoice = widgets.Combobox(value=triggerChoiceList[0], choices=triggerChoiceList, label='Acquisition Setup')
exposure_Time = dict(value=20., min=15., max=1000., step=1.)  # value, min, max, step
startBottom = widgets.ToggleButton(text='Start/Stop Live', value=False)
snapBottom = widgets.PushButton(text='Snap', value=False)
triggerChoice = widgets.ComboBox(value=triggerChoiceList[0],
                                 choices=triggerChoiceList, label='Trigger ype: ')
exposureTime = widgets.FloatSpinBox(**exposure_Time, label='Exposure time (ms): ')
liveGUI = widgets.Container(widgets=[triggerChoice, exposureTime,
                                     widgets.Container(widgets=[startBottom, snapBottom], layout='horizontal')])
startBottom.changed.connect(connect_triggerBottom)
exposureTime.changed.connect(connect_exposureTime)
triggerChoice.changed.connect(connect_triggerChoice)
snapBottom.changed.connect(connect_snapBottom)

# GUI 2. ND acq

def minute2Time(minute: float):
    return '%i:%i:%.1f' % (minute // 60, minute % 60 // 1, minute % 60 % 1 * 60)

def calcEstimateTime():
    time = LoopStep[0].value * (firstPhaseNum.value + secondPhaseNum.value) * LoopStep[1].value
    estimateTime.value = minute2Time(time)


firstPhase = widgets.Container(widgets=[widgets.CheckBox(value=False, text=key) for key in acq_setup.keys()],
                               label='1st phase', layout='horizontal')
secondPhase = widgets.Container(widgets=[widgets.CheckBox(value=False, text=key) for key in acq_setup.keys()],
                                label='2nd phase', layout='horizontal')
firstPhaseNum = widgets.FloatSpinBox(value=1, min=1, step=1, label='1st phase number/loop: ')
secondPhaseNum = widgets.FloatSpinBox(value=0, min=0, step=1, label='2nd phase number/loop: ')
PhaseNum = widgets.Container(widgets=[firstPhaseNum, secondPhaseNum])
LoopStep = widgets.Container(widgets=[widgets.FloatSpinBox(value=1, min=0, step=.1, label='Loop time Step (min): '),
                                      widgets.FloatSpinBox(value=1, min=1, step=1, label='Loop number: ')])

estimateTime = widgets.Label(label='Estimate time: ')
calcEstimateTime()

LoopStep.changed.connect(calcEstimateTime)
PhaseNum.changed.connect(calcEstimateTime)
PhaseNum.changed.connect(calcEstimateTime)

# GUI 3. ND pad
# acq_loop = FakeAcq()
# NDSelectionUI = NDRecorderUI(acq_loop, test=True)
# def show_NDSelectionUI():
#     NDSelectionUI.show()

NDSelectionBottom = widgets.PushButton(text='Open location selection', value=False)
# NDSelectionBottom.changed.connect(show_NDSelectionUI)

# GUI 3. save direct
dirSelect = widgets.FileEdit(mode='d', value=os.path.dirname(sys.path[-1]))

# GUI integration
viewer.window.add_dock_widget(liveGUI,
                              area='right', name='Acquisition parameter')
viewer.window.add_dock_widget(widgets.Container(widgets=[dirSelect]),
                              area='right', name='File save directory')
# pos
viewer.window.add_dock_widget(widgets.Container(widgets=[NDSelectionBottom]),
                              area='right', name='Position selection')
viewer.window.add_dock_widget(widgets.Container(widgets=[firstPhase, secondPhase, PhaseNum, LoopStep, estimateTime]),
                              area='right', name='ND setup')



napari.run()
# %%
