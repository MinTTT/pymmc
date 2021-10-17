"""
 @author: Pan M. CHU
"""

# Built-in/Generic Imports
# Own modules
import os
from multi_t_xy_c_acquisiation import PymmAcq
from device.valve.pymm_valve import ValveController

# %%
MICROSCOPE = 'TiE_prior_arduino'  # Ti2E, Ti2E_H, Ti2E_DB, Ti2E_H_LDJ, TiE_prior, Ti2E_LDJ
DIR = r'F:\zjw\20211013_NH2_pECJ3_M5_updownshift'
# POSITION_FILE = r'H:\Image_Data\moma_data\20210505_pECJ3_M5_L3\multipoints.xml'
POSITION_FILE = None

acq_loop = PymmAcq(device=MICROSCOPE)
device_cfg = acq_loop.device_cfg
device_cfg.set_ROI([0, 512, 2048, 820])
device_cfg.set_device_state(shift_type='init_phase')

# device_cfg.prior_core.set_filter_speed_acc(100, 100, 1)
# device_cfg.set_ROI([0, 710, 2048, 1024])
# device_cfg.set_ROI([0, 710, 2048, 1024])
# device_cfg.set_ROI([0, 0, 2048, 2048])

# %%
# acq_loop.nd_recorder.export_pos(DIR)
device_cfg.set_device_state(shift_type='init_phase')

acq_loop.nd_recorder.import_pos(os.path.join(DIR, 'pos.jl'))

acq_loop.open_NDUI()

# %%
device_cfg.set_device_state(shift_type='init_phase')
device_cfg.set_light_path('BF', '100X_External')

time_step = [0, 3, 30]  # [hr, min, s] in fast growth rate
# time_step = [0, 20, 0]  # [hr, min, s] in slow growth rate
flu_step = 6  # very 6 phase loops acq if 0, don't acq a flu channel
time_duration = [72, 0, 0]

acq_loop.time_step = time_step
acq_loop.multi_acq_3c_sync_light(DIR, POSITION_FILE, acq_loop.time_step, flu_step, time_duration)

# if want to stop acq loop
# acq_loop.stop_acq_loop()

# %%
val_contr = ValveController(port='com9')
# val_contr.valve_off()
# if want control valve

val_contr.valve_off([0, 10, 0])  # close valve
# val_contr.valve_on([2, 30, 0])  # open valve

# %%
import threading as thread
import time
import numpy as np

thread_lock = thread.Lock()


def format_time2second(time_fmt: list):
    factor = [60 * 60, 60, 1]
    ts = np.sum([i for i in map(np.multiply, factor, time_fmt)])
    return ts


def countdown(t, step=1, msg='sleeping', msg_finish: str = None):
    """
    a countdown timer print waiting time in second.
    :param trigger: list, a global trigger
    :param t: time lasting for sleeping
    :param step: the time step between the refreshment of screen.
    :param msg:
    :return: None
    """
    CRED = '\033[91m'
    # CGRE = '\033[92m'
    CEND = '\033[0m'
    _current_time = time.time()
    while time.time() - _current_time < t:
        mins, secs = divmod(t + _current_time - time.time(), 60)
        thread_lock.acquire()
        print(CRED + f"""{msg} for {int(mins)}:{int(secs)}.""" + CEND, end='\r')
        thread_lock.release()
        time.sleep(step)
    if msg_finish:
        print(CRED + f"{msg_finish}" + CEND, end='\r')
    return None


def delay_timestep(time_step, new_step, time_delay):
    time_delay_s = format_time2second(time_delay)
    countdown(time_delay_s, msg='Changing Time Step', msg_finish='Time Step Changed')
    for index, t in enumerate(new_step):
        time_step[index] = t
    return


thread.Thread(target=delay_timestep, args=(acq_loop.time_step, [0, 6, 0], [0, 45, 1])).start()
thread.Thread(target=delay_timestep, args=(acq_loop.time_step, [0, 20, 0], [8, 0, 0])).start()


#%%
import numpy as np
import time
device_cfg.mmcore.set_position(device_cfg.AUTOFOCUS_OFFSET, 100)
while True:
    for fov in acq_loop.nd_recorder.positions:
        print(fov)
        device_cfg.move_xyz_pfs(fov)
        time.sleep(10)
