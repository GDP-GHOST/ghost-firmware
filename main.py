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
    # Camera stuff
    # camera = camera_manager.Camera()
    # camera.initialise()
    # before = time.perf_counter() # not the best practice since variable reassigned later, but debug
    # frames = camera.get_images()
    # after = time.perf_counter()
    # load_performance_time = after - before
    # print(f'{Messages.LOG} Time taken to load {len(frames)} is : {load_performance_time:.6f} s')
    # # Detection stuff
    
    # detector = detection.Detector()
    # frames_to_analyse = frames
    # before = time.perf_counter()
    # masks = detector.detect_across_multiple(frames_to_analyse)
    # after = time.perf_counter()
    # performance_time = after - before
    # print(f'{Messages.LOG} Time taken to detect {len(frames_to_analyse)} frames: {performance_time:.6f} s')

    # plt.imshow(masks[0], cmap='bone') # cmap bone for black and white images
    # plt.show()

    # blob_detection_frames = detector.get_blob_detections(frames_to_analyse)
    ################################
    gens = synthetetic_gen.Generator()
    gens.gen_blank_img((200, 200, 3))
    gens.generate_object_screen((1, 1), (25, 25), Shapes.SQUARE)
    plt.imshow(gens.get_generated_img())
    plt.show()
    #camera.create_gif(blob_detection_frames)

main()