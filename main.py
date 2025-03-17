import camera_manager
import detection
import time #debug purposes & performance tests

def main():
    # Camera stuff
    camera = camera_manager.Camera()
    camera.initialise()
    frames = camera.get_images()
    print(len(frames))
    # Detection stuff
    detector = detection.Detector()
    differences = detector.detect(frames)
    print(len(differences))

main()