# Synthetic generator
import numpy as np
import cv2 as cv
from util.constants import *
from util.messages import *

class Generator:
    def __init__(self):
        self.generated_image = None

    def initialise(self, size):
        self.gen_blank_img(size)
    
    # ensure size is a tuple height x length
    def gen_blank_img(self, size):
        self.generated_image = np.zeros(size, np.uint8)
        self.generated_image[:] = (0, 0, 0) # blakc image
    
    # WARNING: Make sure gen_blank_img() was used before calling this function
    # Intensity is a number always 0.0<i<=1.0, 0.0, will just be a black pixel
    def add_white_pixel(self, position, itensity:float):
        self.generated_image[position[0]][position[1]] = (itensity * 255, itensity * 255, itensity * 255)

    # TODO: add multiple shapes, shape is from Shapes defined in constants.py, CIRCLES?
    # Dimension kernel is the "area" size in which the shape will appear in, everything limited to it. if shape is random, then
    # the intensities and pixel density will be randomised in that area. WARNING: too small like 2x2 pixel is VERY small
    # position start for squares and rectangle is from the conner and circles is from the centre, might change this later...
    def generate_object_screen(self, position_start, dimension_kernel, shape:Shapes):
        match shape:
            case Shapes.SQUARE:
                cv.rectangle(self.generated_image, position_start, (position_start[0] + dimension_kernel[0], position_start[1] + dimension_kernel[1]), (255, 255, 255), -1)
                # for i in range(dimension_kernel): # no need for a second loop since it is a square. TODO: Rectangles 2 different loops?
                #     position_x = position_start[0] + i
                #     self.add_white_pixel(position_start, 1.0)
            case Shapes.RECTANGLE:
                pass
            case Shapes.RANDOM:
                pass


    def get_generated_img(self):
        return self.generated_image

        