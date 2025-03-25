import camera_manager
import detection
import matplotlib.pylab as plt
from util.messages import *
import cv2 as cv
import time #debug purposes & performance tests
from PIL import Image
import synthetetic_gen
from util.constants import *

def main():
    # CAMERA TEST TEMPLATE CODE form stakc overflow: 
    camera = camera_manager.Camera()
    camera.initialise()
    # camera.preview()
    camera.video_without_preview()

main()