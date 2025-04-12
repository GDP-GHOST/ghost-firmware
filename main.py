import camera_manager
import detection
import matplotlib.pylab as plt
from util.messages import *
import cv2 as cv
import time #debug purposes & performance tests
from PIL import Image
import numpy as np

def main():
    # Camera stuff
    camera = camera_manager.Camera()
    camera.initialise()
    before = time.perf_counter() # not the best practice since variable reassigned later, but debug
    frames = camera.get_images()
    after = time.perf_counter()
    load_performance_time = after - before
    print(f'{Messages.LOG} Time taken to load {len(frames)} is : {load_performance_time:.6f} s')
    
    # Detection stuff
    detector = detection.Detector()
    frames_to_analyse = frames[200:202]
    
    flow = detector.flow_computation(frames_to_analyse[0], frames_to_analyse[1])
    # plt.imshow(frames_to_analyse[0])
    # plt.show()
    magnitude, angle = cv.cartToPolar(flow[..., 0], flow[..., 1])
    # plt.imshow(np.log(magnitude/magnitude.max()), cmap='hsv_r')
    # plt.show()
    print(magnitude.max(), magnitude.min())

    rgb = detector.view_flow(flow)

    motion_threshold = np.c_[np.linspace(0.3, 1, 800)].repeat(1000, axis=-1)
    mask = detector.get_motion_mask(magnitude, motion_thresh=motion_threshold)

    plt.imshow(mask, cmap='gray')
    plt.show()

    # plt.imshow(rgb*50) # show noise stuff
    # plt.show()

    blob_detection = detector.get_blob_detection_opt([mask])
    print(blob_detection[0].shape)
    plt.imshow(blob_detection[0])
    plt.show()

    #blobs = detector.get_movement_mask(frames[:8])
    framed = detector.get_movement_image(frames[:8])
    # plt.imshow(blobs[0])
    # plt.show()
    plt.imshow(framed[0])
    plt.show()
    # camera.create_gif(framed)



    # before = time.perf_counter()
    # masks = detector.detect_across_multiple(frames_to_analyse)
    # after = time.perf_counter()
    # performance_time = after - before
    # print(f'{Messages.LOG} Time taken to detect {len(frames_to_analyse)} frames: {performance_time:.6f} s')

    # plt.imshow(masks[10], cmap='bone') # cmap bone for black and white images
    # plt.show()

    #blob_detection_frames = detector.get_blob_detections(frames_to_analyse)
    #camera.create_gif(blob_detection_frames)

main()