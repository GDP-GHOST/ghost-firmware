""" 
    File: detection.py
    Author: Gianluca Borgo (gbg20@soton.ac.uk)

    Libraries: OpenCV (v4.10.0.84), Numpy (v2.0.1)
    Python Version: 3.13.0

    Program Version: 0.2 (according to new architecture)

    Description: Detect objects based on light intensity and movement.

    Instructions: File should act as a "API" as it is a bridge between the numerous algorithms applied. Functions such as detect()
    are subject to change over time, so ensure that you have the most up-to-date version.

    Each new version (merged into main) will increase the version counter.
    
    TODO: 
        - Implement both reference frames moving detection. For now it works only if the camera is fixed.
        
"""

import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import os
from PIL import Image
from util.messages import *

class Detector:
    def __init__(self):
        pass
    
    # frame1 and frame2 should be gray images, here the code is written as such frame2 is considered "after" frame and 
    # "frame1" is considered "before". WARNING: Import to get the order right, or else you will get motion going the wrong
    # way.
    def difference(self, frame1, frame2):
        return cv.subtract(frame2, frame1)
    
    # Frames need to turn from color to gray, since the algorithm uses gray scale images compared against each other
    def gray_frame(self, frame):
        img_color = cv.cvtColor(frame, cv.COLOR_BGR2RGB)            
        img_gray = cv.cvtColor(img_color, cv.COLOR_RGB2GRAY)
        return img_gray
    
    # frames is a list of frames. Function returns the differences between any given amount of frames
    # as long as there are enough frames to check (>=2)
    def detect(self, frames:list):
        if len(frames) < 2:
            print(f"{Messages.ERROR} Not enough frames given to detect. Need at least 2.")
            quit()

        differences = []

        for i in range(len(frames) - 1):
            diff = self.difference(self.gray_frame(frames[i]), self.gray_frame(frames[i+1]))
            differences.append(diff)
        return differences
    
    