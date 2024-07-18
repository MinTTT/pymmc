



"""

This file stores the paramters of the microscope

"""



"""
Light   TriggerMap
Red 0b00000001
Green	0b00000010
Cyan	0b00000100
Teal	0b00001000
Blue	0b00010000
UV	0b00100000
Yellow	0b01000010
Phase	0b10000000
"""

COM_PriorScan = 4
COM_Arduino = 'COM13'

trigger_device = {'camera': 'TUCam',
                  'flu': 'Spectra',
                  'dia': 'X-Cite120PC',
                  'filter': 'TIFilterBlock1'}  # this depends on the devices of microscopes

position_device = {'z': 'TIZDrive', 'pfs_state': 'TIPFSStatus', 'pfs_offset': 'TIPFSOffset'}


trigger_map = {'phase': 0b10000000,
               'none': 0b00000000,
               'red': 0b00000001,
               'green': 0b00000010,
               'cyan': 0b00000100,
               'teal': 0b00001000,
               'blue': 0b00010000,
               'violet': 0b00100000}

# Note some keys in the dictionary may name sensitive that depends on one the devices properties if the microscopes
channels = {'bf': {'exciterSate': 'phase', 'exposure': 25, 
                   'intensity': {'LampIntensity': 24}, 
                   'filter': None, 'colormap': 'gray'},
            'green': {'exciterSate': 'cyan', 'exposure': 20, 
                      'intensity': {'Cyan_Level': 20}, 
                      'filter': {'State': '1'}, 'colormap': 'green'},
            'red': {'exciterSate': 'green', 'exposure': 100, 
                    'intensity': {'Green_Level': 50}, 
                    'filter': {'State': '1'}, 'colormap': 'red'},
            'cyan': {'exciterSate': 'blue', 'exposure': 200, 
                    'intensity': {'Blue_Level': 20}, 
                    'filter': {'State': '4'}, 'colormap': 'cyan'},
            'yellow': {'exciterSate': 'teal', 'exposure': 100, 
                    'intensity': {'Teal_Level': 20}, 
                    'filter': {'State': '4'}, 'colormap': 'yellow'},
            'red2': {'exciterSate': 'green', 'exposure': 200, 
                    'intensity': {'Green_Level': 100}, 
                    'filter': {'State': '4'}, 'colormap': 'red'},
            }

# This can be acquired by function in module: pymm.get_loaded_devices_property()
device_properties = {'COM10': ['AnswerTimeout', 'BaudRate', 'DTR', 'DataBits', 'DelayBetweenCharsMs', 'Description',
                               'Fast USB to Serial', 'Handshaking', 'Name', 'Parity', 'StopBits', 'Verbose'],
                     'COM3': ['AnswerTimeout', 'BaudRate', 'DTR', 'DataBits', 'DelayBetweenCharsMs', 'Description',
                              'Fast USB to Serial', 'Handshaking', 'Name', 'Parity', 'StopBits', 'Verbose'],
                     'TUCam': ['Binning', 'CameraID', 'CameraName', 'Description', 'Exposure',
                               'Exposure_Auto Adjustment', 'Fan', 'FlipH', 'FlipV', 'Gain', 'Image Adjustment Contrast',
                               'Image Adjustment DPC', 'Image Adjustment Gamma', 'Image Adjustment Left  Levels',
                               'Image Adjustment Right Levels', 'LEDMode', 'Name', 'Output Trigger Delay',
                               'Output Trigger Edge Mode', 'Output Trigger Kind', 'Output Trigger Port',
                               'Output Trigger Width', 'PixelClock', 'PixelType', 'SaveImage', 'Targeting Level',
                               'Temperature', 'TransposeCorrection', 'TransposeMirrorX', 'TransposeMirrorY',
                               'TransposeXY', 'Trigger Delay', 'Trigger Edge Mode', 'Trigger Exposure Mode',
                               'Trigger Mode'],
                     'Spectra': ['Blue_Enable', 'Blue_Level', 'Cyan_Enable', 'Cyan_Level', 'Description',
                                 'Green_Enable', 'Green_Level', 'Name', 'Port', 'Red_Enable', 'Red_Level', 'SetLE_Type',
                                 'State', 'Teal_Enable', 'Teal_Level', 'Violet_Enable', 'Violet_Level', 'White_Enable',
                                 'White_Level', 'YG_Filter'],
                     'TIScope': ['DeviceAddress', 'DeviceIndex', 'DriverVersion', 'FirmwareVersion', 'SoftwareVersion'],
                     'TIEpiShutter': ['Name', 'State'],
                     'TINosePiece': ['ExtraDelayMs', 'Label', 'Name', 'State'],
                     'TICondenserCassette': ['ExtraDelayMs', 'Label', 'Name', 'State'],
                     'TIFilterBlock1': ['ExtraDelayMs', 'Label', 'Name', 'State'],
                     'TILightPath': ['ExtraDelayMs', 'Label', 'Name', 'State'],
                     'TIZDrive': ['Name', 'Speed', 'Tolerance'],
                     'TIPFSOffset': ['Name', 'Position'],
                     'TIPFSStatus': ['FullFocusTimeoutMs', 'FullFocusWaitAfterLockMs', 'Name', 'State', 'Status'],
                     'X-Cite120PC': ['Exposure-Time [s]', 'LampHours', 'LampIntensity', 'LockFrontPanel', 'Name',
                                     'Port', 'Shutter-State', 'ShutterSoftwareVersion', 'Trigger'],
                     'Core': ['AutoFocus', 'AutoShutter', 'Camera', 'ChannelGroup', 'Focus', 'Galvo', 'ImageProcessor',
                              'Initialize', 'SLM', 'Shutter', 'TimeoutMs', 'XYStage']}
