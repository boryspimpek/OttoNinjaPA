import urandom # type: ignore
from servo_lib import RobotConfig, ServoController
import time

cfg    = RobotConfig()
servos = cfg.servos
robot  = cfg.robot

RF, RL, RA = cfg.RF, cfg.RL, cfg.RA
LF, LL, LA = cfg.LF, cfg.LL, cfg.LA

def return_to_neutral():
    servos.set_speeds(LF, 0, RF, 0)  # oba serwa 360 stop
    servos.move_to_angles(LL, 60, RL, 120)  # oba serwa kąt neutralny

def tilt_right():
    servos.move_to_angles(LL, 10, RL, 86)  # oba serwa przechył w prawo
    time.sleep(0.5)

def tilt_left():
    servos.move_to_angles(LL, 90, RL, 170)  # oba serwa przechył w lewo
    time.sleep(0.5)

def ride_position():
    servos.move_to_angles(LL, 150, RL, 30)  # pozycja do jazdy
    time.sleep(0.5)

def left_leg_swing():
    tilt_right()
    servos.set_speed(RF, -5)

def right_leg_swing():
    tilt_left()
    servos.set_speed(LF, 5)

def wave(delay=0.3):
    tilt_right()
    time.sleep(delay)
    servos.move_to_angles(LL, 60)
    time.sleep(delay)
    servos.move_to_angles(LL, 20)
    time.sleep(delay)
    tilt_left()
    time.sleep(delay)
    servos.move_to_angles(RL, 120)
    time.sleep(delay)
    servos.move_to_angles(RL, 160)
    time.sleep(delay)
    return_to_neutral()

def steps(delay=0.3):
    for i in range(3):
        servos.move_to_angles(LL, 80, RL, 170)
        time.sleep(delay)  
        servos.move_to_angles(LL, 10, RL, 100)
        time.sleep(delay)
    return_to_neutral()

def tilt(delay=0.3):
    for i in range(3):
        servos.move_to_angles(LL, 80, RL, 140)
        time.sleep(delay)
        servos.move_to_angles(LL, 40, RL, 100)
        time.sleep(delay)
    return_to_neutral()

def weird(iterations=3):
    for _ in range(iterations):
        servos.set_speeds(LF, urandom.randint(5, 10), RF, urandom.randint(5, 10))
        time.sleep(1)
    return_to_neutral()

bt1_pressed = False
bt2_pressed = False
bt3_pressed = False
bt4_pressed = False
bt5_pressed = False
bt6_pressed = False
bt7_pressed = False
bt8_pressed = False
sw3_pressed = False

while True:
    if cfg.tick():

        # ------------------ SW 3 -----------------
        if robot.sw3 and not sw3_pressed:
            ride_position()
            sw3_pressed = True
        elif not robot.sw3 and sw3_pressed:
            return_to_neutral()
            sw3_pressed = False

        if sw3_pressed:
            servos.set_speed(LF, ServoController.map_joystick(robot.ly, cfg.JOY_DEAD, cfg.LF_SERVO_MIN, cfg.LF_SERVO_MAX))
            servos.set_speed(RF, ServoController.map_joystick(-robot.ry, cfg.JOY_DEAD, cfg.RF_SERVO_MIN, cfg.RF_SERVO_MAX))

        # ------------------ bt1 -----------------
        if robot.bt1 and not bt1_pressed:
            steps()
            bt1_pressed = True
        elif not robot.bt1 and bt1_pressed:
            bt1_pressed = False

        # ------------------ bt2 -----------------
        if robot.bt2 and not bt2_pressed:
            weird()
            bt2_pressed = True
        elif not robot.bt2 and bt2_pressed:
            bt2_pressed = False

        # ------------------ bt4 -----------------
        if robot.bt4 and not bt4_pressed:
            right_leg_swing()
            bt4_pressed = True
        elif not robot.bt4 and bt4_pressed:
            return_to_neutral()
            bt4_pressed = False
        
        # ------------------ bt5 -----------------
        if robot.bt5 and not bt5_pressed:
            tilt()
            bt5_pressed = True
        elif not robot.bt5 and bt5_pressed:
            bt5_pressed = False

        # ------------------ bt6 -----------------
        if robot.bt6 and not bt6_pressed:
            wave()
            bt6_pressed = True
        elif not robot.bt6 and bt6_pressed:
            bt6_pressed = False

        # ------------------ bt8 -----------------
        if robot.bt8 and not bt8_pressed:
            left_leg_swing()
            bt8_pressed = True
        elif not robot.bt8 and bt8_pressed:
            return_to_neutral()
            bt8_pressed = False



    time.sleep_ms(10)