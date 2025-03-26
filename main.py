import camera_manager
import detection
from util.messages import *
import cv2 as cv
import time #debug purposes & performance tests
from PIL import Image
import synthetetic_gen
from util.constants import *

def main():
    camera = camera_manager.Camera()
    camera.initialise()
    #camera.preview() # Camera preview only works if screen is enabled, opencv headless might cause some issues.
    camera.video_without_preview()

main()
