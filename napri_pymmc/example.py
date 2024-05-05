"""
magicgui with threadworker
==========================

An example of calling a threaded function from a magicgui ``dock_widget``.
Note: this example requires python >=m 3.9

.. tags:: gui
"""

#%%
import os
from typing import Annotated
from magicgui import magic_factory, widgets
from skimage import data
from skimage.feature import blob_log

import napari
from napari.qt.threading import FunctionWorker, thread_worker
from napari.types import ImageData, LayerDataTuple

from skimage import data
import numpy as np
import time
from threading import Thread
from napari.qt.threading import thread_worker
from typing import Optional

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
#%%

class randCamera:
    buffer : Optional[np.ndarray] = None
    def __init__(self, buffer_size: int = 1, y_size: int = 512,
                 x_size: int = 512,  time_step: float = 1) -> None:
        
        self.buffer_size = buffer_size
        self.y_size = y_size
        self.x_size = x_size
        self.time_step = time_step
        self.current_index: int = -1
        self.buffer = np.zeros((buffer_size, y_size, x_size), dtype=np.uint16)
        self.live_flag = False

    def snap(self) -> None:
        self.current_index = (self.current_index + 1) % self.buffer_size
        self.buffer[self.current_index, ...] = np.random.random((self.y_size, self.x_size))* 2**16
        return None
    
    @threaded
    def _live(self):
        self.live_flag = True
        while self.live_flag:
            self.current_index = (self.current_index + 1) % self.buffer_size
            self.buffer[self.current_index, ...] = np.random.random((self.y_size, self.x_size))* 2**16
            time.sleep(self.time_step/1000)
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
        if camera.current_index !=index_0:
            index_0 = camera.current_index
            time.sleep(1/100)
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
triggerChoiceList = ['None']
exposure_Time = dict(value=20., min=15., max=1000., step=1.)  # value, min, max, step
startBottom = widgets.ToggleButton(text='Start/Stop Live', value=False)
triggerChoice = widgets.ComboBox(value=triggerChoiceList[0],
                               choices=triggerChoiceList, label='Trigger ype: ')
exposureTime = widgets.FloatSpinBox(**exposure_Time, label='Exposure time (ms): ')
liveGUI = widgets.Container(widgets=[triggerChoice, exposureTime, startBottom])
startBottom.changed.connect(connect_triggerBottom)
exposureTime.changed.connect(connect_exposureTime)
triggerChoice.changed.connect(connect_triggerChoice)
viewer.window.add_dock_widget(liveGUI, area='right', name='Acquisition parameter')
# GUI 2. ND acq
acq_setup = dict(phase=dict(exposure=30, intensity=10, trigger=0),
                 green=dict(exposure=30, intensity=10, trigger=0),
                 red=dict(exposure=30, intensity=10, trigger=0))

def calcEstimateTime():
    time = LoopStep[0].value * (firstPhaseNum.value + secondPhaseNum.value) * LoopStep[1].value
    estimateTime.value = minute2Time(time)

firstPhase = widgets.Container(widgets=[widgets.CheckBox(value=False, text=key) for key in acq_setup.keys()], label='1st phase')
secondPhase = widgets.Container(widgets=[widgets.CheckBox(value=False, text=key) for key in acq_setup.keys()], label='2nd phase')
firstPhaseNum = widgets.FloatSpinBox(value=1, min=1, step=1, label='1st phase number/loop: ')
secondPhaseNum = widgets.FloatSpinBox(value=0, min=0, step=1, label='2nd phase number/loop: ')
PhaseNum = widgets.Container(widgets=[firstPhaseNum, secondPhaseNum])
LoopStep = widgets.Container(widgets=[widgets.FloatSpinBox(value=1, min=0, step=.1, label='Loop time Step (min): '),
                                      widgets.FloatSpinBox(value=1, min=1, step=1, label='Loop number: ')])
minute2Time = lambda minute :'%i:%i:%.1f' % (minute//60,  minute%60//1, minute%60%1*60)
estimateTime = widgets.Label(label='Estimate time: ')
calcEstimateTime()
viewer.window.add_dock_widget(widgets.Container(widgets=[firstPhase, secondPhase, PhaseNum, LoopStep, estimateTime]),
                              area='right', name='ND setup')
LoopStep.changed.connect(calcEstimateTime)
PhaseNum.changed.connect(calcEstimateTime)
PhaseNum.changed.connect(calcEstimateTime)
# GUI 3. save direct
dirSelect = widgets.FileEdit(mode='d', value=os.path.dirname(__file__))
viewer.window.add_dock_widget(widgets.Container(widgets=[dirSelect]),
                              area='right', name='File save directory')



napari.run()
# %%
 