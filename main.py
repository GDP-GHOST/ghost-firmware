import camera_manager
import detection
import matplotlib.pylab as plt
from util.messages import *
import cv2 as cv
import time #debug purposes & performance tests

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
    frames_to_analyse = frames[10:14]
    before = time.perf_counter()
    differences, masks = detector.detect_across_multiple(frames_to_analyse)
    after = time.perf_counter()
    performance_time = after - before
    print(f'{Messages.LOG} Time taken to detect {len(frames_to_analyse)} frames: {performance_time:.6f} s')

    #plt.imshow(differences[0][0], cmap='bone') # cmap bone for black and white images
    plt.imshow(masks[0], cmap='bone') # cmap bone for black and white images
    plt.show()
    blobs = detector.get_contour_blob(masks[0])
    mask = cv.cvtColor(masks[0], cv.COLOR_GRAY2RGB)
    for box in blobs:
        print(box)
        x1,y1,x2,y2,area = box
        cv.rectangle(mask, (x1, y1), (x2, y2), (255, 0, 0), 1)
    plt.imshow(mask)
    plt.show()

main()