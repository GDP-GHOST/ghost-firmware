# TODO: Camera live code, for now this function fetches from files.
import os
from util.constants import *

class Camera:
    def __init__(self):
        self.camera = None #placeholder

    # Gets an ordered list of the files in the folder
    def get_file_list(self):
        root, dirs, files = next(os.walk(IMAGE_DIRECTORY, topdown=True))
        files = [ os.path.join(root, f) for f in files ]
        sorted_files = sorted(files, key = lambda x : int(x[-7:-4]))
        return sorted_files
