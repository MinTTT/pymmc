"""
This code used for acq TCXY

Micro-manager config: Fulab-TiE.cfg
"""

# %%
from Acq_module import AcqControl, imgSave, core
import numpy as np
import time
# from napari.qt.threading import create_worker, FunctionWorker
import threading
from pymm_uitls import countdown
import os

# % Init device
device_ctrl = AcqControl(mmCore=core)
trigger = device_ctrl.acqTrigger
# %%
# Time duration in Seconds
time_duration = 3600 * 5
time_step = 5 * 60
# save dir 
save_dir = r"D:\zjw\20230704_5_60XRedInit_L3strins_TimeLapse_Test"
# Channel
channels_set = {'red': {'exciterSate': 'green', 'exposure': 200, 'intensity': {'Green_Level': 50}},
                'green': {'exciterSate': 'cyan', 'exposure': 40, 'intensity': {'Cyan_Level': 50}},
                'bf': {'exciterSate': 'phase', 'exposure': 30, 'intensity': {'Intensity': 24}}}

# Select pos

trigger.channel_dict = channels_set
trigger.set_channel('bf')
device_ctrl.napari.open_xyz_control_panel()
trigger.show_live()
#%%
# device_ctrl.nd_recorder.import_pos(os.path.join(save_dir, 'pos.jl'))
trigger.stop_live()

# %%
# acq
loops_num = int(time_duration / time_step)
channels_num = len(list(device_ctrl.acqTrigger.channel_dict.keys()))
P_num = device_ctrl.nd_recorder.position_number
channels_name = list(trigger.channel_dict.keys())

# create image buffer
trigger.img_buff = np.zeros((loops_num, P_num, channels_num,
                             *trigger.img_shape), dtype=trigger.img_depth)
# crate dir
if os.path.isdir(save_dir) is False:
    os.mkdir(save_dir)
for p_i in range(P_num):
    fov_dict = os.path.join(save_dir, f'fov_{p_i}')
    if os.path.isdir(fov_dict) is False:
        os.mkdir(fov_dict)
# Export positions 
device_ctrl.nd_recorder.export_pos(save_dir)

for c_i, c_name in enumerate(channels_name):
    device_ctrl.napari.update_layer([trigger.img_buff[:, :, c_i, ...], c_name])


def thread_run(args):
    print('Start Acq Loops.')
    loops_num, P_num, time_step, channels_name, obj, stop_flag, = args
    device_ctrl = obj
    trigger = obj.acqTrigger
    img_saver = imgSave()
    start_time = time.time()
    for loop_i in range(loops_num):
        loopstart_time = time.time()
        for p_i in range(P_num):
            pos = device_ctrl.nd_recorder.positions[p_i]
            device_ctrl.move_xyz_pfs(pos)
            print(f'Move to Pos {p_i}.')
            for c_i, c_name in enumerate(channels_name):
                trigger.set_channel(c_name)
                img, meta = trigger.snap(show=False)
                trigger.img_buff[loop_i, p_i, c_i, ...] = img
            device_ctrl.napari.update_index([0, loop_i])
            device_ctrl.napari.update_index([1, p_i])
            # save file
            save_img = trigger.img_buff[loop_i, p_i, ...]
            img_saver.save(os.path.join(save_dir, f'fov_{p_i}'),
                           't.ome.tif', save_img, 'CYX', 
                           dict(Description={'Times':[time.time()], 'Labels': channels_name}, 
                                Channel={'Name':['GFP', 'mCherry', 'Phase']},
                                TimeIncrement=time_step,
                                TimeIncrementUnit='s'),
                                )
        # waiting next loop
            
        next_loop_time = (loop_i + 1) * time_step + start_time
        # loop_time =  loop_stoptime - loopstart_time
        loop_stoptime = time.time()
        waiting_time = next_loop_time - loop_stoptime
        msg = countdown(waiting_time, 1, stop_flag)
        if msg == 1:
            return None
    return None


stop_flag = [False]
# acq_worker = create_worker(thread_run, 
#                            (loops_num, P_num, channels_name, 
#                            device_ctrl, stop_flag))
# acq_worker.start()
# napari.run()
acq_thread = threading.Thread(target=thread_run, 
                              args=((loops_num, P_num, time_step,
                                    channels_name, 
                                    device_ctrl, stop_flag),))
acq_thread.start()
# for loop_i in range(loops_num):

#     for p_i in range(P_num):
#         pos = device_ctrl.nd_recorder.positions[p_i]
#         device_ctrl.move_xyz_pfs(pos)
#         print(f'Move to Pos {p_i}, {pos}')
#         for c_i, c_name in enumerate(channels_name):
#             trigger.set_channel(c_name)
#             image_obj, meta = trigger.snap(show=False)
#             trigger.img_buff[loop_i, p_i, c_i, ...] = image_obj
#         device_ctrl.napari.update_index([0, loop_i])
#         device_ctrl.napari.update_index([1, p_i])
#     time.sleep(5)    
#%%  Stop ACQ
stop_flag[0] = True
# %%
