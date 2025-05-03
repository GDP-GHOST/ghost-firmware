from util.constants import *
from util.messages import *
import math
import time
import motor_manager

def fix_mirror_position(motor1:motor_manager.Motor, motor2:motor_manager.Motor):
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
                motor2.set_position(n_small_target, 0, 1, 100000000)
                change_val_small = n_small_target

            # =====  BIG MIRROR  (horizontal correction) ==========
            x_m       = c + d * math.sqrt(1.0 - sin_theta * sin_theta)
            x_inc     = Kx * x_m
            n_big_target = round(X_CENTRE - x_inc)
            if change_val_big == None:
                change_val_big = n_big_target

            if change_val_big != n_big_target:
                success = motor1.set_position(n_big_target, 0, 1, 100000000) # second parameter is relative mode and third is immediately = true
                change_val_big = n_big_target
        print(f'{Messages.LOG} Finalised target following')
        return True

def state_machine(motor1:motor_manager.Motor, motor2:motor_manager.Motor):
    enabled = True
    state = State.OPEN
    while enabled:
        match state:
            case State.OPEN:
                success1 = motor1.connect()
                success2 = motor2.connect()
                if success1 and success2:
                    state = State.ACTIVATE # go to the next state
                else:
                    print(f'{Messages.ERROR} Motor failed connect [motor1, motor2] {success1, success2}')
                    state = State.ERROR
                    
            case State.ACTIVATE:
                success1 = motor1.activate()
                success2 = motor2.activate()
                if success and success2:
                    state = State.CONFIGURE
                else:
                    print(f'{Messages.ERROR} Motor failed activate [motor1, motor2] {success1, success2}')
                    state = State.ERROR
            
            case State.CONFIGURE:
                # configure parmeters -> velocity, acceleration, deceleration, timeout
                success1 = motor1.configure(1, 1, 1, 20000000)
                success2 = motor2.configure(1, 1, 1, 20000000)
                if success:
                    state = State.ENABLE
                else:
                    print(f'{Messages.ERROR} Motor failed configure [motor1, motor2] {success1, success2}')
                    state = State.ERROR
            
            case State.ENABLE:
                success1 = motor1.enable()
                success2 = motor2.enable()
                if success:
                    state = State.MOVE
                else:
                    print(f'{Messages.ERROR} Motor failed enable [motor1, motor2] {success1, success2}')
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
                success = fix_mirror_position(motor1, motor2)
                if success:
                    state = State.DISABLE
                else:
                    state = State.ERROR
            
            case State.DISABLE:
                print("Position after movement: ", motor1.get_position())
                success1 = motor1.disable()
                success2 = motor2.disable()
                if success:
                    state = State.CLOSE
                else:
                    print(f'{Messages.ERROR} Motor failed disable [motor1, motor2] {success1, success2}')
                    state = State.ERROR

            case State.CLOSE:
                success = motor1.close()
                success = motor2.close()
                enabled = False

            case State.ERROR:
                print(f'{Messages.ERROR} Error executing demo')
                state = State.CLOSE

def main():
    controller1 = motor_manager.Motor(1)
    controller2 = motor_manager.Motor(29)

    # observation motor1 is big motor and motor2 is small motor

    state_machine(controller1, controller2)

main()