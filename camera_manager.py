# TODO: Camera live code, for now this function fetches from files.
import os
from util.constants import *
import cv2 as cv
from util.messages import *
from PIL import Image

class Camera:
    def __init__(self):
        self.camera = None #placeholder
        self.images = []

    # Worth noting that the folder in which these images are being taken from
    # are of frames, if using anything else might cause the rest of the algorithm to break.
    def initialise(self):
        for file in self.get_file_list():
            frame = cv.imread(file)
            self.images.append(frame)
        print(f'{Messages.SUCCESS} Initialised camera object')

    # Gets an ordered list of the files in the folder
    def get_file_list(self):
        root, dirs, files = next(os.walk(IMAGE_DIRECTORY, topdown=True))
        files = [ os.path.join(root, f) for f in files ]
        sorted_files = sorted(files, key = lambda x : int(x[-7:-4]))
        return sorted_files
    
    def get_images(self):
        return self.images
    
    def create_gif(self, frames):
        gif = []
        for img in frames:
            gif.append(Image.fromarray(img))
        gif[0].save('detect.gif', save_all=True,optimize=False, append_images=gif[1:], loop=0)
