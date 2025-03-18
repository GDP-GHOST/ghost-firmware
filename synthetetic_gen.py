# Synthetic generator
import numpy as np
from util.constants import *
from util.messages import *

class Generator:
    def __init__(self):
        self.generated_image = None
    
    # ensure size is a tuple height x length
    def gen_blank_img(self, size):
        self.generated_image = np.zeros(size, np.uint8)
        self.generated_image[:] = (255, 255, 255) # blakc image

        return self.generated_image
    
    # WARNING: Make sure gen_blank_img() was used before calling this function
    def add_white_pixel(self, position, itensity):
        self.generated_image[position[0]][position[1]] = (0, 0, 0)
        