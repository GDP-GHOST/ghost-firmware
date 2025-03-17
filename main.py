import camera_manager
import detection
import matplotlib.pylab as plt
from util.messages import *
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
    frames_to_analyse = frames[10:12]
    before = time.perf_counter()
    differences = detector.detect(frames_to_analyse)
    after = time.perf_counter()
    performance_time = after - before
    print(f'{Messages.LOG} Time taken to detect {len(frames_to_analyse)} frames: {performance_time:.6f} s')

    plt.imshow(differences[0], cmap='bone') # cmap bone for black and white images
    plt.show()

main()