import camera_manager
import detection
from util.messages import *
import cv2 as cv
import time #debug purposes & performance tests
from PIL import Image
import synthetetic_gen
from util.constants import *
import motor_manager

def main():
    controller = motor_manager.Motor()
    keyhandle, ret, device_error, p_error_code = controller.connect()
    if keyhandle != 0:
        if device_error.value == 0:
            ret = controller.set_profile(500, 1000, 1000)
            success = controller.get_position()
            ret = controller.enable_state()
            ret = controller.set_position(10000, 20)
            ret = controller.disable_state()
            ret = controller.get_position()
        controller.close()
    else:
        print(f'{Messages.ERROR} Could not open COM port. Keyhandle:%8d, Error: %#5.8x' % (keyhandle, p_error_code.value))
main()
