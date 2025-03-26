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

main()
