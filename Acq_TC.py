"""
This code used for acq TCXY


"""

#%%
from Acq_module import AcqControl, imgSave, core
import numpy as np
import time
import threading
from pymm_uitls import countdown
import os
#% Init device
device_ctrl = AcqControl(mmCore=core)
trigger = device_ctrl.acqTrigger
#%%
# Time duration in Seconds
time_duration = 3600 * 5
time_step = 5 * 60
# save dir 
save_dir = r"D:\zjw\20230704_3_60XRedInit_L3strins_TimeLapse"
# Channel
channels_set = {'red': {'exciterSate': 'green', 'exposure': 200, 'intensity': {'Green_Level': 50}},
                'green': {'exciterSate': 'cyan', 'exposure': 40, 'intensity': {'Cyan_Level': 20}},
                'bf': {'exciterSate': 'phase', 'exposure': 25, 'intensity': {'Intensity': 24}}}

# Select pos

trigger.channel_dict = channels_set
trigger.set_channel('bf')
device_ctrl.napari.open_xyz_control_panel()
trigger.show_live()
#%%
trigger.stop_live()

#%%
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

for c_i, c_name in enumerate(channels_name):
    device_ctrl.napari.update_layer([trigger.img_buff[:,:, c_i,...], c_name])


def thread_run(args):
    loops_num, P_num, channels_name, obj, stop_flag = args
    device_ctrl = obj
    trigger = obj.acqTrigger
    img_saver = imgSave()
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
                           dict(Description={'Times':[time.time()], 'Labels': channels_name}, ))
        # waiting next loop
        loop_stoptime = time.time()    
        loop_time =  loop_stoptime - loopstart_time
        msg = countdown(time_step - loop_time, 1, stop_flag)
        if msg == 1:
            return None
    return None

stop_flag = [False]
acq_thread = threading.Thread(target=thread_run, 
                              args=((loops_num, P_num, channels_name, 
                                    device_ctrl, stop_flag),))
acq_thread.start()
# for loop_i in range(loops_num):
    
#     for p_i in range(P_num):
#         pos = device_ctrl.nd_recorder.positions[p_i]
#         device_ctrl.move_xyz_pfs(pos)
#         print(f'Move to Pos {p_i}, {pos}')
#         for c_i, c_name in enumerate(channels_name):
#             trigger.set_channel(c_name)
#             img, meta = trigger.snap(show=False)
#             trigger.img_buff[loop_i, p_i, c_i, ...] = img
#         device_ctrl.napari.update_index([0, loop_i])
#         device_ctrl.napari.update_index([1, p_i])
#     time.sleep(5)    
#%%
stop_flag[0] = True
# %%
import tifffile
from tifffile import TiffFile
from lxml import etree
def getOMETiffDescription2dict(img: TiffFile):
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
    node = etree.fromstring(img.pages[0].description.encode('utf-8'), parser=parser)
    desc = elem2dict(node)['Image']['Description']

    return eval(desc)


def elem2dict(node, attributes=True):
    """
    Convert an lxml.etree node tree into a dict.
    """
    result = {}
    if attributes:
        for item in node.attrib.items():
            key, result[key] = item

    for element in node.iterchildren():
        # Remove namespace prefix
        key = etree.QName(element).localname

        # Process element as tree element if the inner XML contains non-whitespace content
        if element.text and element.text.strip():
            value = element.text
        else:
            value = elem2dict(element)
        if key in result:
            if type(result[key]) is list:
                result[key].append(value)
            else:
                result[key] = [result[key], value]
        else:
            result[key] = value
    return result

save_dir = r"D:\zjw\20230704_3_60XRedInit_L3strins_TimeLapse"
target_dirt = r'Y:\fulab_zc_6\AGAR_PAD'
dir_base_name = os.path.basename(save_dir)
image_save_dirt = os.path.join(target_dirt, dir_base_name)
fov_dirs = [dir.name for dir in os.scandir(save_dir) if dir.is_dir()]

fov_dir = fov_dirs[0]
img_list = [img.name for img in os.scandir(os.path.join(save_dir, fov_dirs[0]))
            if img.name.split('.')[-1] == 'tif']
img_list.sort(key=lambda name: int(name.split('.')[0].split('_')[-1]))
image_data = []
time_data = []
for img_name in img_list:
    img = tifffile.TiffFile(os.path.join(save_dir, fov_dir, img_name))
    
    description = getOMETiffDescription2dict(img)
    time_data += description['Times']
image_shape = img.pages[0].shape
image_data_type = img.pages[0].dtype
image_buffer = np.empty((len(time_data), *image_shape), dtype=image_data_type)
        # if isinstance(value, str):
            # print(value.split('=')[0])
        # print(value.split('=')[0])
        # if value.split('=')[0] == 'datetime':
        #     time_data.append(value.split('=')[-1])



# %%
