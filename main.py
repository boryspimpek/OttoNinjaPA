from servo_lib import RobotConfig, ServoController
import time

cfg    = RobotConfig()
servos = cfg.servos
robot  = cfg.robot

RF, RL, RA = cfg.RF, cfg.RL, cfg.RA
LF, LL, LA = cfg.LF, cfg.LL, cfg.LA

def return_to_neutral():
    servos.set_speed(LF, 0)         # servo 360 stop
    servos.set_angle(LL, 60) 
    servos.set_speed(RF, 0)         # servo 360 stop
    servos.set_angle(RL, 120) 

def left_leg_swing():
    servos.set_angle(LL, 20)
    servos.set_angle(RL, 80)
    time.sleep(0.5)
    servos.set_speed(RF, 10)

def right_leg_swing():
    servos.set_angle(LL, 100)
    servos.set_angle(RL, 160)
    time.sleep(0.5)
    servos.set_speed(LF, 10)

bt1_pressed = False
bt5_pressed = False
walking = False  # tryb chodzenia aktywny

while True:
    if cfg.tick():
        # --- Joysticki ---
        if not walking:
            servos.set_speed(LF, ServoController.map_joystick(robot.ly, cfg.JOY_DEAD, cfg.LF_SERVO_MIN, cfg.LF_SERVO_MAX))
            servos.set_speed(RF, ServoController.map_joystick(-robot.ry, cfg.JOY_DEAD, cfg.RF_SERVO_MIN, cfg.RF_SERVO_MAX))

        # ------------------ bt1 -----------------
        if robot.bt1 and not bt1_pressed:
            left_leg_swing()
            walking = True
            bt1_pressed = True
        elif not robot.bt1 and bt1_pressed:
            return_to_neutral()
            walking = False
            bt1_pressed = False
        
        # ------------------ bt2 -----------------
        if robot.bt5 and not bt5_pressed:
            right_leg_swing()
            walking = True
            bt5_pressed = True
        elif not robot.bt5 and bt5_pressed:
            return_to_neutral()
            walking = False
            bt5_pressed = False

    time.sleep_ms(10)