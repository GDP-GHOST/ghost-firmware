from ctypes import *
from util.constants import *
from util.messages import *
import time
import math
cdll.LoadLibrary(MOTOR_SO)
epos4 = CDLL(MOTOR_SO)


# TODO: A lot of error handling will be missing form this first iteration of the code, this is
# just to continue testing stuff in building 32 (our testing location in southampton)
# Add error codes messages. Funcitons will return 1 if sucess and 0 if failure
class Motor:
    def __init__(self, node_id, usb):
        self.node_id = node_id # change this later to the constants on file, for now testing
        self.usb = usb
        self.keyhandle = 0
        self.ret = 0
        self.p_error_code = c_uint()
        self.p_device_error_code = c_uint() # p means pointer, required to handle the stuff being returned from the EPOS library
        self.moving = False

    def connect(self):
        print(f'{Messages.LOG} Opening Port...')
        # TODO: (Less Priority) Turn parameters here into constants
        self.keyhandle = epos4.VCS_OpenDevice(b'EPOS4', b'MAXON SERIAL V2', b'USB', self.usb, byref(self.p_error_code))
        #self.keyhandle = epos4.VCS_OpenDeviceDlg(byref(self.p_error_code))

        if self.keyhandle != 0: # documentation states that anything nonzero is success
            print(f"{Messages.LOG} Connection established at keyhandle {self.keyhandle}")
            return 1
        
        self.evaluate_error() # if the system throws an error, this functuin should catch it
        return 0 # 0 is false, then device didnt connect properly, go to error state

    def activate(self):
        print(f'{Messages.LOG} Activating position mode...')
        success = epos4.VCS_ActivateProfilePositionMode(self.keyhandle, self.node_id, byref(self.p_error_code))
        if success != 0:
            print(f'{Messages.SUCCESS} Activated position mode')
            return 1
        self.evaluate_error()
        return 0

    def configure(self, velocity, acceleration, deceleration, timeout):
        success = epos4.VCS_SetPositionProfile(self.keyhandle, self.node_id, velocity, acceleration, deceleration, byref(self.p_error_code))
        print("Success in configure: ", success)

        if success != 0:
            print(f'{Messages.DEBUG} Profile set with a velocity of {velocity} [rpm], acceleration of {acceleration} [rpm] and {deceleration} [rpm]')
            return 1
        print("HERE?")
        self.evaluate_error()
        return 0 # fixed by making sure it matches epos software
    
    def enable(self):
        enabled = c_bool()

        error = self.check_device_error()

        if error == 1:
            success = epos4.VCS_SetEnableState(self.keyhandle, self.node_id, byref(self.p_error_code))

            if success != 0:
                success = epos4.VCS_GetEnableState(self.keyhandle, self.node_id, byref(enabled), byref(self.p_error_code))

                if enabled.value == 1:
                    print(f'{Messages.SUCCESS} Device enabled')
                    return 1
                else:
                    return 0
                
        print(f'{Messages.ERROR} Failed to enable device')
        return 0
    
    def disable(self):
        disabled = c_bool()

        error = self.check_device_error()

        if error == 1:
            success = epos4.VCS_SetDisableState(self.keyhandle, self.node_id, byref(self.p_error_code))

            if success != 0:
                success = epos4.VCS_GetDisableState(self.keyhandle, self.node_id, byref(disabled), byref(self.p_error_code))

                if disabled.value == 1:
                    print(f'{Messages.SUCCESS} Device disabled')
                    return 1
                
        print(f'{Messages.ERROR} Failed to disable device')
        return 0

    
    # absolute and imediately are from maxon documentation. imediately means movement starts instantaneously
    def set_position(self, target_position, absolute_movement, imediately, timeout):
        success = epos4.VCS_MoveToPosition(self.keyhandle, self.node_id, target_position, absolute_movement, imediately, byref(self.p_error_code))

        if success != 0:

            self.moving = True

            reached = self.check_reached(timeout)
            if reached:
                return 1
            else:
                print(f'{Messages.WARNING} Failed to reach requested position')
        else:
            print(f'{Messages.ERROR} Failed to set position')
            
        return 0
    
    def check_reached(self, timeout):
        time_passed = 0
        p_target_reached = c_bool()
        while self.moving:
            if time_passed >= timeout: #TODO: This doesnt have a certain control of how many in the loop, add in future
                print(f'{Messages.ERROR} Timeout for motor movement')
                self.moving = False
                return 0
            
            success = epos4.VCS_GetMovementState(self.keyhandle, self.node_id, byref(p_target_reached), byref(self.p_error_code))
            if success != 0:

                error = self.evaluate_error()

                if not error:
                    if p_target_reached.value == 1:
                        return 1
                    time_passed += 1
                    print("Motor position before sleep (SLEEP REMOVED): ", self.get_position())
                    #time.sleep(1) # potentially need to find non-blocking ways
                else:
                    print(f'{Messages.ERROR} Could not command in movement')
            else:
                print(f'{Messages.ERROR} Error using VCS_GetMovementState() function')
        return 0
    
    def check_device_error(self):
        success = epos4.VCS_GetDeviceErrorCode(self.keyhandle, self.node_id, 1, byref(self.p_device_error_code), byref(self.p_error_code))

        if self.p_device_error_code.value == 0:
            self.evaluate_error()
            return 1
        return 0
                



    def connect_old(self):
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

    def clear_faults(self):
        sucess = epos4.VCS_ClearFault(self.keyhandle, self.node_id, byref(self.p_error_code))#attempt to clear errors > sets motor to disable state
        if sucess == 0: # documnetation states that non-zero is sucess so
            print(f'{Messages.LOG} Error code closing port: %#5.8x' % self.p_error_code.value)
            return
        self.enable_state() # after clearing faults the system goes to disabled, enable again
        # TODO???? enable the profile again for moving? might be required here or another function


    def close(self):
        self.ret = epos4.VCS_CloseDevice(self.keyhandle, byref(self.p_error_code))
        print(f'{Messages.LOG} Error code closing port: %#5.8x' % self.p_error_code.value)

    def set_profile(self, velocity, acceleration, deceleration):
        print(f'{Messages.LOG} Setting profiles')
        ret = epos4.VCS_ActivateProfilePositionMode(self.keyhandle, self.node_id, byref(self.p_error_code))
        ret = epos4.VCS_SetPositionProfile(self.keyhandle, self.node_id, velocity, acceleration, deceleration, byref(self.p_error_code)) # 500, 1000, 1000
        print("Sucess at set_profile: ", ret)
        return ret

    def get_position(self):
        pPositionIs=c_long()
        pErrorCode=c_uint()

        ret=epos4.VCS_GetPositionIs(self.keyhandle, self.node_id, byref(pPositionIs), byref(pErrorCode))

        if ret == 1:
            print(f'{Messages.LOG} Position Actual Value: %d [inc]' % pPositionIs.value) # TODO: Remove this later
            return pPositionIs.value
        else:
            print(f'{Messages.ERROR} GetPositionIs failed')

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
    
    def check_position_reached(self):
        p_target_reached=c_bool()
        sucess = epos4.VCS_GetMovementState(self.keyhandle, self.node_id, byref(p_target_reached), byref(self.p_error_code))
        if sucess == 0:
            print(f'{Messages.ERROR} Failed to acquire GetMovemementState()')
            return 0
        return p_target_reached.value # 1 if reached 0 if not
    
    def evaluate_error(self):
        error_info = ' ' * 40
        if self.p_error_code.value != 0x0:
            epos4.VCS_GetErrorInfo(self.p_error_code.value, error_info, 40)
            print('Error Code %#5.8x, description: %s' % (self.p_error_code.value, error_info))
            return 1
        return 0

    def set_position_old(self, position, timeout):
        moving = False
        # The new position will begin immediately, which is why one of the flag is set to 1
        # TODO: Change in the future to be configured, for now reduce parameters
        sucess = epos4.VCS_MoveToPosition(self.keyhandle, self.node_id, position, 0, 1, byref(self.p_error_code))
        if sucess == 0:
            print(f'{Messages.ERROR} Failed to set motor position.')
            return 0
        else:
            moving = True
        
        time = 0
        while moving:
            if self.evaluate_error():
                print(f'{Messages.ERROR} Error during motor set position command')
                moving = False
                return 0

            if time >= timeout:
                moving = False
                print(f'{Messages.ERROR} timeout motor reaching target')
                return 0
            
            if self.check_position_reached() == 1:
                moving = False
                print(f'{Messages.SUCCESS} Reached target') #TODO: remove this print, for now kept for debug
            
            time += 1
            
        return 1
    
    def test_motor(self):
        ret = epos4.VCS_MoveToPosition(self.keyhandle, self.node_id, 2000, 0, 0, byref(self.p_error_code))
        ret = self.check_acknowledgment()
        ret = epos4.VCS_MoveToPosition(self.keyhandle, self.node_id, -2000, 0, 0, byref(self.p_error_code))
        ret = self.check_acknowledgment()
        return ret
    
    def demo(self):
        enabled = True
        state = State.OPEN
        while enabled:
            match state:
                case State.OPEN:
                    success = self.connect()
                    if success:
                        state = State.ACTIVATE # go to the next state
                    else:
                        state = State.ERROR
                        
                case State.ACTIVATE:
                    success = self.activate()
                    if success:
                        state = State.CONFIGURE
                    else:
                        state = State.ERROR
                
                case State.CONFIGURE:
                    # configure parmeters -> velocity, acceleration, deceleration, timeout
                    success = self.configure(1, 1, 1, 20000000)
                    if success:
                        state = State.ENABLE
                    else:
                        print("HI")
                        state = State.ERROR
                
                case State.ENABLE:
                    success = self.enable()
                    if success:
                        state = State.MOVE
                    else:
                        state = State.ERROR
                
                case State.MOVE:
                    # set_position parameters ->target_position, absolute_movement, imediately, timeout. timeout not used in config
                    print("Position: ", self.get_position())
                    pProfileVelocity = c_uint()
                    pProfileAcceleration = c_uint()
                    pProfileDeceleration = c_uint()
                    test = epos4.VCS_GetPositionProfile(self.keyhandle, self.node_id, pProfileVelocity, pProfileAcceleration, pProfileDeceleration, self.p_error_code)
                    print("Value acceleratioN: ", pProfileVelocity.value)           
                    success = self.set_position(512, 1, 1, 10000000)
                    if success:
                        state = State.DISABLE
                    else:
                        state = State.ERROR
                
                case State.DISABLE:
                    time.sleep(20)
                    print("Position after movement: ", self.get_position())
                    success = self.disable()
                    if success:
                        state = State.CLOSE
                    else:
                        state = State.ERROR

                case State.CLOSE:
                    success = self.close()
                    enabled = False

                case State.ERROR:
                    print(f'{Messages.ERROR} Error executing demo')
                    state = State.CLOSE

    ####### DEMO Saturday (03/05/2025)
    def fix_mirror_position(self):
        # function to fix the big and small mirror position to go according the tracked distance
        # will create a BLOCKING (using sleep) loop for 60 fps

        a, b = 0.029315, 3.948505           # y(θ) parameters (metres)
        c, d = 2.93475, 0.71435             # x(θ) parameters (metres)

        v_obj = 0.0925                # m s⁻¹ downward
        H_screen = 3.772                 # m screen height
        T_RUN = H_screen / v_obj      # 40.8 s sweep

        N_SMALL = 94                    # small‑mirror steps top→bottom

        Kx = 90 / 7.28             # 12.3626 screen‑inc per metre
        X_CENTRE = 45                    # centre of the 0‑90 increment scale

        # ---- pre‑compute anchor angles ---------------------------------
        theta0 = math.asin(a / b)                 # θ when y=0 m
        thetaF = math.asin((a - H_screen) / b)    # θ when y=H_screen
        DTH_PER_STEP = (thetaF - theta0) / N_SMALL

        run_trajectory = True
        running_time = 40.7
        # running
        period = 1.0 / 60.0               # 60 Hz tick  (16 ms)
        t0     = time.perf_counter()
        next_tick = t0

        # cumulative step counters that we've *already* issued
        n_small_cmd = 0
        n_big_cmd   = 0

        change_val_small = None
        change_val_big = None

        while run_trajectory:
            now = time.perf_counter() #60fps timer
            if now < next_tick:
                time.sleep(next_tick - now)
            next_tick += period
            t = now - t0

            if t >= running_time:
                run_trajectory = False

            sin_theta = (a - v_obj * t) / b
            theta     = math.asin(sin_theta)          # + branch

            # =====  SMALL MIRROR  (vertical) ======================
            n_small_target = round(N_SMALL * (theta - theta0) /
                                (thetaF - theta0))
            if change_val_small == None:
                change_val_small = n_small_target

            if change_val_small != n_small_target:
                #send_small_steps(n_small_target) # Implement small mirror
                change_val_small = n_small_target

            # =====  BIG MIRROR  (horizontal correction) ==========
            x_m       = c + d * math.sqrt(1.0 - sin_theta * sin_theta)
            x_inc     = Kx * x_m
            n_big_target = round(X_CENTRE - x_inc)
            if change_val_big == None:
                change_val_big = n_big_target

            if change_val_big != n_big_target:
                success = self.set_position(n_big_target, 0, 1, 100000000) # second parameter is relative mode and third is immediately = true
                change_val_big = n_big_target
        print(f'{Messages.LOG} Finalised target following')
        return True

    def recorded_track(self):
        enabled = True
        state = State.OPEN
        while enabled:
            match state:
                case State.OPEN:
                    success = self.connect()
                    if success:
                        state = State.ACTIVATE # go to the next state
                    else:
                        state = State.ERROR
                        
                case State.ACTIVATE:
                    success = self.activate()
                    if success:
                        state = State.CONFIGURE
                    else:
                        state = State.ERROR
                
                case State.CONFIGURE:
                    # configure parmeters -> velocity, acceleration, deceleration, timeout
                    success = self.configure(1, 1, 1, 20000000)
                    if success:
                        state = State.ENABLE
                    else:
                        state = State.ERROR
                
                case State.ENABLE:
                    success = self.enable()
                    if success:
                        state = State.MOVE
                    else:
                        state = State.ERROR
                
                case State.MOVE:
                    # set_position parameters ->target_position, absolute_movement, imediately, timeout. timeout not used
                    # print("Position: ", self.get_position())
                    # pProfileVelocity = c_uint()
                    # pProfileAcceleration = c_uint()
                    # pProfileDeceleration = c_uint()
                    # test = epos4.VCS_GetPositionProfile(self.keyhandle, self.node_id, pProfileVelocity, pProfileAcceleration, pProfileDeceleration, self.p_error_code)
                    # print("Value acceleratioN: ", pProfileVelocity.value)           
                    # success = self.set_position(200, 1, 1, 10000000)
                    #self.fix_mirror_position()
                    self.set_position(400, 1, 1, 10000000)
                    if success:
                        state = State.DISABLE
                    else:
                        state = State.ERROR
                
                case State.DISABLE:
                    print("Position after movement: ", self.get_position())
                    success = self.disable()
                    if success:
                        state = State.CLOSE
                    else:
                        state = State.ERROR

                case State.CLOSE:
                    success = self.close()
                    enabled = False

                case State.ERROR:
                    print(f'{Messages.ERROR} Error executing demo')
                    state = State.CLOSE
    
    def big_mirror(self):
            enabled = True
            state = State.OPEN
            while enabled:
                match state:
                    case State.OPEN:
                        success = self.connect()
                        if success:
                            state = State.ACTIVATE # go to the next state
                        else:
                            state = State.ERROR
                            
                    case State.ACTIVATE:
                        success = self.activate()
                        if success:
                            state = State.CONFIGURE
                        else:
                            state = State.ERROR
                    
                    case State.CONFIGURE:
                        # configure parmeters -> velocity, acceleration, deceleration, timeout
                        success = self.configure(1, 1, 1, 20000000)
                        if success:
                            state = State.ENABLE
                        else:
                            print("HI")
                            state = State.ERROR
                    
                    case State.ENABLE:
                        success = self.enable()
                        if success:
                            state = State.MOVE
                        else:
                            state = State.ERROR
                    
                    case State.MOVE:
                        # set_position parameters ->target_position, absolute_movement, imediately, timeout. timeout not used in config
                        print("Position: ", self.get_position())
                        pProfileVelocity = c_uint()
                        pProfileAcceleration = c_uint()
                        pProfileDeceleration = c_uint()
                        test = epos4.VCS_GetPositionProfile(self.keyhandle, self.node_id, pProfileVelocity, pProfileAcceleration, pProfileDeceleration, self.p_error_code)
                        print("Value acceleratioN: ", pProfileVelocity.value)           
                        success = self.set_position(512, 1, 1, 10000000)
                        if success:
                            state = State.DISABLE
                        else:
                            state = State.ERROR
                    
                    case State.DISABLE:
                        time.sleep(20)
                        print("Position after movement: ", self.get_position())
                        success = self.disable()
                        if success:
                            state = State.CLOSE
                        else:
                            state = State.ERROR

                    case State.CLOSE:
                        success = self.close()
                        enabled = False

                    case State.ERROR:
                        print(f'{Messages.ERROR} Error executing demo')
                        state = State.CLOSE
        
    def small_mirror(self):
        enabled = True
        state = State.OPEN
        while enabled:
            match state:
                case State.OPEN:
                    success = self.connect()
                    if success:
                        state = State.ACTIVATE # go to the next state
                    else:
                        state = State.ERROR
                        
                case State.ACTIVATE:
                    success = self.activate()
                    if success:
                        state = State.CONFIGURE
                    else:
                        state = State.ERROR
                
                case State.CONFIGURE:
                    # configure parmeters -> velocity, acceleration, deceleration, timeout
                    success = self.configure(1, 1, 1, 20000000)
                    if success:
                        state = State.ENABLE
                    else:
                        print("HI")
                        state = State.ERROR
                
                case State.ENABLE:
                    success = self.enable()
                    if success:
                        state = State.MOVE
                    else:
                        state = State.ERROR
                
                case State.MOVE:
                    # set_position parameters ->target_position, absolute_movement, imediately, timeout. timeout not used in config
                    print("Position: ", self.get_position())
                    pProfileVelocity = c_uint()
                    pProfileAcceleration = c_uint()
                    pProfileDeceleration = c_uint()
                    test = epos4.VCS_GetPositionProfile(self.keyhandle, self.node_id, pProfileVelocity, pProfileAcceleration, pProfileDeceleration, self.p_error_code)
                    print("Value acceleratioN: ", pProfileVelocity.value)           
                    success = self.set_position(300, 1, 1, 10000000)
                    if success:
                        state = State.DISABLE
                    else:
                        state = State.ERROR
                
                case State.DISABLE:
                    time.sleep(20)
                    print("Position after movement: ", self.get_position())
                    success = self.disable()
                    if success:
                        state = State.CLOSE
                    else:
                        state = State.ERROR

                case State.CLOSE:
                    success = self.close()
                    enabled = False

                case State.ERROR:
                    print(f'{Messages.ERROR} Error executing demo')
                    state = State.CLOSE
