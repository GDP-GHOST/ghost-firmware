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
    controller.open_device()
    print(controller.get_motor_position())
    # 
    # controller.set_motor_position(10000, 10000, 20000, 5000)
    controller.close_device()
main()
