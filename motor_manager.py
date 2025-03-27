from ctypes import *
from util.constants import *
from util.messages import *
cdll.LoadLibrary(MOTOR_SO)
epos4 = CDLL(MOTOR_SO)


# TODO: A lot of error handling will be missing form this first iteration of the code, this is
# just to continue testing stuff in building 32 (our testing location in southampton)
# Add error codes messages
class Motor:
    def __init__(self):
        self.node_id = 1 # change this later to the constants on file, for now testing
        self.keyhandle = 0
        self.ret = 0
        self.p_error_code = c_uint()
        self.p_device_error_code = c_uint() # p means pointer, required to handle the stuff being returned from the EPOS library

    def connect(self):
        print(f'{Messages.LOG} Opening Port...')
        self.keyhandle = epos4.VCS_OpenDevice(b'EPOS4', b'MAXON SERIAL V2', b'USB', b'USB0', byref(self.p_error_code))
        if self.keyhandle != 0:
            print(f"{Messages.LOG} Connection established at keyhandle {self.keyhandle}")
            self.ret = epos4.VCS_GetDeviceErrorCode(self.keyhandle, self.node_id, 1, byref(self.p_device_error_code), byref(self.p_error_code))
            print(f'{Messages.LOG} Device Error: %#5.8x' % self.p_device_error_code.value)
            if self.p_device_error_code.value != 0:
                print(f'{Messages.ERROR} Motor in error state: %#5.8x' % self.p_device_error_code.value)
                self.close() #ensure that teh port is closed
        return self.keyhandle, self.ret, self.p_device_error_code
    
    def close(self):
        self.ret = epos4.VCS_CloseDevice(self.keyhandle, byref(self.p_error_code))
        print(f'{Messages.LOG} Error code closing port: %#5.8x' % self.p_error_code.value)

    def set_profile(self):
        print(f'{Messages.LOG} Setting profiles')
        ret = epos4.VCS_ActivateProfilePositionMode(self.keyhandle, self.node_id, byref(self.p_error_code))
        ret = epos4.VCS_SetPositionProfile(self.keyhandle, self.node_id, 500, 1000, 1000, byref(self.p_error_code) )

    def get_position(self):
        pPositionIs=c_long()
        pErrorCode=c_uint()

        ret=epos4.VCS_GetPositionIs(self.keyhandle, self.node_id, byref(pPositionIs), byref(pErrorCode))

        if ret == 1:
            print(f'{Messages.LOG} Position Actual Value: %d [inc]' % pPositionIs.value)
            return 1
        else:
            print(f'{Messages.ERROR} GetPositionIs failed')
            return 0
