
# ID is the object that is being tracked unique id
# TRACKABLE is if the object can still be tracked within the image. Updated to TRUE only when the object has appeared for multiple frames
# this is achieved by using the calculated area (TODO: in the future will also check distance travelled and direction). If the AREA is equal
# to AVR_AREA (updated every frame by doing area/amount_frames_passed_since_first_det)
# X and Y are updated every frame a given motion is found, but the width and height will not change.
class Obj:
    def __init__(self, ID:int, TRACKABLE:bool, X:int, Y:int, WIDTH:int, HEIGHT:int, AREA:int):
        self.ID = ID
        self.TRACKABLE = TRACKABLE
        self.X = X
        self.Y = Y
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.AREA = AREA
