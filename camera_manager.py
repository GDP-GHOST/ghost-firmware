# TODO: Camera live code, for now this function fetches from files.
import os
from util.constants import *
import cv2 as cv

class Camera:
    def __init__(self):
        self.camera = None #placeholder
        self.images = None

    # Worth noting that the folder in which these images are being taken from
    # are of frames, if using anything else might cause the rest of the algorithm to break.
    def initialise(self):
        for file in self.get_file_list():
            frame = cv.imread(file)
            self.images.append(frame)

    # Gets an ordered list of the files in the folder
    def get_file_list(self):
        root, dirs, files = next(os.walk(IMAGE_DIRECTORY, topdown=True))
        files = [ os.path.join(root, f) for f in files ]
        sorted_files = sorted(files, key = lambda x : int(x[-7:-4]))
        return sorted_files
    
    def get_images(self):
        return self.images
