PARENT_DIRECTORY = r'C:\Users\gianb\Desktop\Personal\Year 5\GDP\ghost-firmware'
IMAGE_DIRECTORY = r'C:\Users\gianb\Desktop\Personal\Year 5\GDP\Programming\Datasets\ezgif-1-e2bfa5822d-jpg' # Outside repository as mostly used for debug

CAMERA_ID = 0 # on my laptop svbony is 1, but pi will probably be 0

MOTOR_SO = '.\EposCmd64.dll'#EPOS_Linux_Library/libEposCmd.so.6.6.1.0' # This path will change on linux or windows, depends where you downloaded the maxon stuMTOff
MOTOR_NODE_ID = 29
MOTOR_KEYHANDLE = 0
MOTOR_RET = 0 
MOTOR_PORT = b'USB0' #for linux this will be some tty port in /dev/ check what is opened
BAUDRATE = 1000000
TIMEOUT = 500

class Shapes:
    # Standard shapes
    # TODO: Add more shapes
    SQUARE = 1
    RECTANGLE = 2
    CIRCLE = 3
    RANDOM = 4

class State:
    ERROR = -1
    OPEN = 0
    ACTIVATE = 1
    CONFIGURE = 2
    ENABLE = 3
    MOVE = 4
    DISABLE = 5
    CLOSE = 6

