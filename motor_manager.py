from ctypes import *
from util.constants import *


# TODO: A lot of error handling will be missing form this first iteration of the code, this is
# just to continue testing stuff in building 32 (our testing location in southampton)
# Add error codes messages
class Motor:
    def __init__(self):
        cdll.LoadLibrary(MOTOR_SO)
        self.motor_interface = CDLL(MOTOR_SO)

        self.node_id = MOTOR_NODE_ID
        self.keyhandle = MOTOR_KEYHANDLE
        self.ret = MOTOR_RET
        self.p_error_code = c_uint()
        self.p_device_error_code = c_uint() # p means pointer, required to handle the stuff being returned from the EPOS library

    def open_device(self):
        # TODO: put all the hard coded into constants file, maxon serial v2 etc
        self.keyhandle = self.motor_interface.VCS_OpenDevice(b'EPOS4', b'MAXON SERIAL V2', b'USB', MOTOR_PORT, byref(self.p_error_code))
        self.motor_interface.VCS_SetProtocolStackSettings(self.keyhandle, BAUDRATE, TIMEOUT, byref(self.p_error_code)) # TODO BAUDRATE ad TIMEOUT need contained variables?
        self.motor_interface.VCS_ClearFault(self.keyhandle, self.node_id, byref(self.p_error_code)) # if there is any faults, clear them
        self.motor_interface.VCS_ActivateProfilePositionMode(self.keyhandle, self.node_id, byref(self.p_error_code)) # start mode for positioning the motors
        self.motor_interface.VCS_SetEnableState(self.keyhandle, self.node_id, byref(self.p_error_code)) # finally enable the device
    
    def close_device(self):
        self.motor_interface.VCS_SetDisableState(self.keyhandle, self.node_id, byref(self.p_error_code)) # disable device
        self.motor_interface.VCS_CloseDevice(self.keyhandle, byref(self.p_error_code)) # close device

    def set_motor_position(self, acceleration, deceleration, target_position, target_speed):
        while True:
            if target_speed != 0:
                self.motor_interface.VCS_SetPositionProfile(self.keyhandle, self.node_id, target_speed, acceleration, deceleration, byref(self.p_error_code)) # set profile parameters
                self.motor_interface.VCS_MoveToPosition(self.keyhandle, self.node_id, target_position, True, True, byref(self.p_error_code)) # move to position
            elif target_speed == 0:
                self.motor_interface.VCS_HaltPositionMovement(self.keyhandle, self.node_id, byref(self.p_error_code)) # halt motor
            true_position = self.get_motor_position()
            if true_position == target_position:
                break
    
    def get_motor_position(self):
        pPositionIs=c_long()
        pErrorCode=c_uint()
        ret=self.motor_interface.VCS_GetPositionIs(self.keyhandle, self.node_id, byref(pPositionIs), byref(pErrorCode))
        return pPositionIs.value # motor steps