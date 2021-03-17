# Created by Diego Alonso Alvarez on the 12th July 2020
# Copyright (c) 2020 Imperial College London

from ctypes import WinDLL, create_string_buffer
import os
import sys


os.chdir(r'D:\python_code\pymmc\device\prior_stage\x64/')
path = "PriorScientificSDK.dll"
if os.path.exists(path):
    SDKPrior = WinDLL(path)
else:
    raise RuntimeError("DLL could not be loaded.")

rx = create_string_buffer(1000)
realhw = False


def cmd(msg):
    print(msg)
    ret = SDKPrior.PriorScientificSDK_cmd(
        sessionID, create_string_buffer(msg.encode()), rx
    )
    if ret:
        print(f"Api error {ret}")
    else:
        print(f"OK {rx.value.decode()}")

    input("Press ENTER to continue...")
    return ret, rx.value.decode()


ret = SDKPrior.PriorScientificSDK_Initialise()
if ret:
    print(f"Error initialising {ret}")
    sys.exit()
else:
    print(f"Ok initialising {ret}")


ret = SDKPrior.PriorScientificSDK_Version(rx)
print(f"dll version api ret={ret}, version={rx.value.decode()}")


sessionID = SDKPrior.PriorScientificSDK_OpenNewSession()
if sessionID < 0:
    print(f"Error getting sessionID {ret}")
else:
    print(f"SessionID = {sessionID}")


ret = SDKPrior.PriorScientificSDK_cmd(
    sessionID, create_string_buffer(b"dll.apitest 33 goodresponse"), rx
)
print(f"api response {ret}, rx = {rx.value.decode()}")
input("Press ENTER to continue...")


ret = SDKPrior.PriorScientificSDK_cmd(
    sessionID, create_string_buffer(b"dll.apitest -300 stillgoodresponse"), rx
)
print(f"api response {ret}, rx = {rx.value.decode()}")
input("Press ENTER to continue...")


if realhw:
    print("Connecting...")
    # substitute 3 with your com port Id
    cmd("controller.connect 3")

    # test an illegal command
    cmd("controller.stage.position.getx")

    # get current XY position in default units of microns
    cmd("controller.stage.position.get")

    # re-define this current position as 1234,5678
    cmd("controller.stage.position.set 1234 5678")

    # check it worked
    cmd("controller.stage.position.get")

    # set it back to 0,0
    cmd("controller.stage.position.set 0 0")
    cmd("controller.stage.position.get")

    # start a move to a new position, normally you would poll
    # 'controller.stage.busy.get' until response = 0
    cmd("controller.stage.goto-position 1234 5678")

    # example velocity move of 10u/s in both x and y
    cmd("controller.stage.move-at-velocity 10 10")

    # see busy status
    cmd("controller.stage.busy.get")

    # stop velocity move
    cmd("controller.stage.move-at-velocity 0 0")

    # see busy status */
    cmd("controller.stage.busy.get")

    # see new position
    cmd("controller.stage.position.get")

    # disconnect cleanly from controller
    cmd("controller.disconnect")

else:
    input("Press ENTER to continue...")
