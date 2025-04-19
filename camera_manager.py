# TODO: Camera live code, for now this function fetches from files.
import os
from util.constants import *
import cv2 as cv
from util.messages import *
from PIL import Image

class Camera:
    def __init__(self):
        self.camera = None
        self.camera_enabled = False
        self.images = []

    # Worth noting that the folder in which these images are being taken from
    # are of frames, if using anything else might cause the rest of the algorithm to break.
    def initialise(self):
        self.initialise_camera()
        # for file in self.get_file_list():
        #     frame = cv.imread(file)
        #     self.images.append(frame) # Removed for now for testing camera preview
        print(f'{Messages.SUCCESS} Initialised camera object')
    
    def initialise_camera(self):
        print(f"{Messages.LOG} Initialising the camera")
        if CAMERA_USAGE:
            self.camera = cv.VideoCapture(CAMERA_ID) # # WARNING ABOUT THIS NEEDS TO CHMOD the file /dev/video0 with 777 permission
            print(self.camera.isOpened())
            if self.camera.isOpened():
                self.camera_enabled, frame = self.camera.read()
                print(f"{Messages.SUCCESS} Camera Initialised")
            else:
                self.camera_enabled = False # if the camera is some reason disabled
                self.camera.release()
                self.camera = None
                cv.destroyAllWindows()
                print(f"{Messages.ERROR} Camera failed to initialise correctly. Terminating...")
                return
        else:
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
    
    def create_gif(self, frames):
        gif = []
        for img in frames:
            gif.append(Image.fromarray(img))
        gif[0].save('detect_framed.gif', save_all=True,optimize=False, append_images=gif[1:], loop=0)

        # WARNING: Only call this function after initialising the camera object through initialise() function
    def preview(self):
        cv.namedWindow("GHOST")
        while self.camera_enabled:
            self.camera_enabled, frame = self.camera.read()
            cv.imshow("GHOST", frame)
            key = cv.waitKey(20)
            # Pressing esc will terminate the preview window
            if key == 27: 
                self.camera_enabled = False
        cv.destroyWindow("GHOST")
        self.camera.release() # TODO: make a camera shutdown function in case more functions requried
    
    #TODO: IMPLEMENT A WAY TO QUIT THE PROGRAM WITHOUT CNTRL + C
    def video_without_preview(self):
        frame_width = int(self.camera.get(3)) 
        frame_height = int(self.camera.get(4)) 
        
        size = (frame_width, frame_height) 
        video_writer = cv.VideoWriter('test_video.avi',  
                            cv.VideoWriter_fourcc(*'MJPG'), 
                            10, size) 
        
        while self.camera_enabled:
            self.camera_enabled, frame = self.camera.read()
            video_writer.write(frame) 

        video_writer.release()
        self.camera.release()
