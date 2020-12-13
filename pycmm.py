MM_PATH = r'C:/Program Files/Micro-Manager-2.0gamma/'
CONFIG = "mmc2_ti2_light_path.cfg"
import sys

sys.path.insert(0, MM_PATH)
import pymmcore

# import MMCorePy


# %%
# global core
core = pymmcore.CMMCore()
core.setDeviceAdapterSearchPaths([MM_PATH])
core.loadSystemConfiguration(MM_PATH + CONFIG)

core.snapImage()
im = core.getImage()
