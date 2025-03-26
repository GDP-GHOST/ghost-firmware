import ctypes
from util.constants import *

class Motor:
    def __init__(self):
        self.motor_interface = ctypes.CDLL(MOTOR_SO)