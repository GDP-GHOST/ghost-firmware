from ctypes import *
from util.constants import *
from util.messages import *
import time
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
        return self.keyhandle, self.ret, self.p_device_error_code, self.p_error_code
    
    def close(self):
        self.ret = epos4.VCS_CloseDevice(self.keyhandle, byref(self.p_error_code))
        print(f'{Messages.LOG} Error code closing port: %#5.8x' % self.p_error_code.value)

    def set_profile(self):
        print(f'{Messages.LOG} Setting profiles')
        ret = epos4.VCS_ActivateProfilePositionMode(self.keyhandle, self.node_id, byref(self.p_error_code))
        ret = epos4.VCS_SetPositionProfile(self.keyhandle, self.node_id, 500, 1000, 1000, byref(self.p_error_code))
        return ret

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

    def check_acknowledgment(self):
        # From official maxxon documentation this function
        ObjectIndex=0x6041
        ObjectSubindex=0x0
        NbOfBytesToRead=0x02
        pNbOfBytesRead=c_uint()
        pData=c_uint()
        pErrorCode=c_uint()

        # Setpoint Acknowledged
        Mask_Bit12=0x1000
        Bit12=0
        i=0

        while True:
            # Read Statusword
            self.get_position()
            ret=epos4.VCS_GetObject(self.keyhandle, self.node_id, ObjectIndex, ObjectSubindex, byref(pData), NbOfBytesToRead, byref(pNbOfBytesRead), byref(pErrorCode))
            Bit12=Mask_Bit12&pData.value

            # Timed out
            if i>20:
                return 0
                break

            if Bit12==Mask_Bit12:
                time.sleep(1)
                i+=1

            # Bit12 reseted = new profile started
            else:
                return 1
                break
    
    def enable_state(self):
        ret = epos4.VCS_SetEnableState(self.keyhandle, self.node_id, byref(self.p_error_code))
        print(f'{Messages.LOG} Enabled motor')
        return ret
    
    def disable_state(self):
        ret = epos4.VCS_SetDisableState(self.keyhandle, self.node_id, byref(self.p_error_code))
        print(f'{Messages.LOG} Disabled motor')
        return ret

    def set_position(self):
        ret = epos4.VCS_MoveToPosition(self.keyhandle, self.node_id, 2000, 0, 0, byref(self.p_error_code))
        ret = self.check_acknowledgment()
        ret = epos4.VCS_MoveToPosition(self.keyhandle, self.node_id, -2000, 0, 0, byref(self.p_error_code))
        ret = self.check_acknowledgment()
        return ret