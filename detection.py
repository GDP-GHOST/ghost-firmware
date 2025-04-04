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
    # way. WARNING: make sure frames are gray scale to make our lives easier for the GDP
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
        masks = []

        for i in range(len(frames) - 1):
            diff = self.difference(self.gray_frame(frames[i]), self.gray_frame(frames[i+1]))
            diff = self.apply_gaussian(diff)
            mask = cv.adaptiveThreshold(diff, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 7, 3)
            mask = self.apply_gaussian(mask)
            differences.append(diff)
            masks.append(mask)

        return differences, masks
    
    # TODO: Add choice to frames amount
    def detect_across_multiple(self, frames:list):
        if len(frames) < 4:
            print(f"{Messages.ERROR} Not enough frames given to detect. Need at least 4.")
            quit()

        differences = []
        masks = []

        for i in range(len(frames) - 3):
            diff_1 = self.difference(self.gray_frame(frames[i]), self.gray_frame(frames[i+1]))
            diff_2 = self.difference(self.gray_frame(frames[i+2]), self.gray_frame(frames[i+3]))
            diff = self.difference(diff_1, diff_2)

            diff = self.apply_gaussian(diff)
            mask = cv.adaptiveThreshold(diff, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 7, 3)
            mask = self.apply_gaussian(mask)
            mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, np.array((5, 5)), iterations=10)
            differences.append(diff)
            masks.append(mask)

        return masks
    
    # Only use this function after difference is applied. WARNING: Expects gray scale image
    # TODO: THIS IS A APPLY MEDIAN not gaussian, whoops
    # TODO: Make so the 3 (kernel size) is passed as parameter
    def apply_gaussian(self, frame):
        return cv.medianBlur(frame, 3) # 3 is the kernel size and must be odd, not sure yet why opencv does that
    
    def get_contour_blob(self, frame): # ensure frame is the masked one
        contours, _ = cv.findContours(frame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_TC89_L1)

        detected = []

        for contour in contours:
            x,y,w,h = cv.boundingRect(contour)
            area = w*h

            # print(area)
            if area > 5: # just abstract number based on the printed areas not sure it works
                detected.append([x, y, x+w, y+h, area])
        
        detected = np.array(detected)
        return detected
    
    def get_blob_detections(self, frames):
        masks = self.detect_across_multiple(frames)
        colored_masks = []
        for mask in masks:
            blobs = self.get_contour_blob(mask)
            mask_color = cv.cvtColor(mask, cv.COLOR_GRAY2RGB)
            for box in blobs:
                x1,y1,x2,y2,area = box
                cv.rectangle(mask_color, (x1, y1), (x2, y2), (255, 0, 0), 1)
            colored_masks.append(mask_color)
        return colored_masks

    

    
    
