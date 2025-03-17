import camera_manager
import detection

def main():
    # Camera stuff
    camera = camera_manager.Camera()
    camera.initialise()
    frames = camera.get_images()

    # Detection stuff
    detector = detection.Detector()
    differences = detector.detect(frames)

main()