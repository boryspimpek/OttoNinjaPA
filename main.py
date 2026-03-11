import urandom # type: ignore
from servo_lib import RobotConfig, ServoController, SCREEN_MAIN, SCREEN_2, SCREEN_3
from moves import RobotMoves
import time

cfg    = RobotConfig()
servos = cfg.servos
robot  = cfg.robot

RF, RL, RA = cfg.RF, cfg.RL, cfg.RA
LF, LL, LA = cfg.LF, cfg.LL, cfg.LA

moves = RobotMoves(servos, LF, RF, LL, RL, LA, RA)

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
            moves.ride_position()
            sw3_pressed = True
        elif not robot.sw3 and sw3_pressed:
            servos.move_to_angles(LL, 60, RL, 120, step=10, delay=0.02)  # powrót do pozycji neutralnej
            sw3_pressed = False

        if sw3_pressed:
            servos.set_speed(LF, ServoController.map_joystick(robot.ly, cfg.JOY_DEAD, cfg.LF_SERVO_MIN, cfg.LF_SERVO_MAX))
            servos.set_speed(RF, ServoController.map_joystick(-robot.ry, cfg.JOY_DEAD, cfg.RF_SERVO_MIN, cfg.RF_SERVO_MAX))

        screen = robot.screen

        if screen == SCREEN_2:
            # ------------------ bt1 -----------------
            if robot.bt1 and not bt1_pressed:
                moves.steps()
                bt1_pressed = True
            elif not robot.bt1 and bt1_pressed:
                bt1_pressed = False

            # ------------------ bt2 -----------------
            if robot.bt2 and not bt2_pressed:
                moves.arms()
                bt2_pressed = True
            elif not robot.bt2 and bt2_pressed:
                bt2_pressed = False

            # ------------------ bt3 -----------------
            if robot.bt3 and not bt3_pressed:
                moves.right_back()
                bt3_pressed = True
            elif not robot.bt3 and bt3_pressed:
                moves.return_to_neutral()
                bt3_pressed = False

            # ------------------ bt4 -----------------
            if robot.bt4 and not bt4_pressed:
                moves.right_forward()
                bt4_pressed = True
            elif not robot.bt4 and bt4_pressed:
                moves.return_to_neutral()
                bt4_pressed = False
            
            # ------------------ bt5 -----------------
            if robot.bt5 and not bt5_pressed:
                moves.tilt()
                bt5_pressed = True
            elif not robot.bt5 and bt5_pressed:
                bt5_pressed = False

            # ------------------ bt6 -----------------
            if robot.bt6 and not bt6_pressed:
                moves.wave()
                bt6_pressed = True
            elif not robot.bt6 and bt6_pressed:
                bt6_pressed = False

            # ------------------ bt7 -----------------
            if robot.bt7 and not bt7_pressed:
                moves.left_back()
                bt7_pressed = True  
            elif not robot.bt7 and bt7_pressed:
                moves.return_to_neutral()
                bt7_pressed = False

            # ------------------ bt8 -----------------
            if robot.bt8 and not bt8_pressed:
                moves.left_forward()
                bt8_pressed = True
            elif not robot.bt8 and bt8_pressed:
                moves.return_to_neutral()
                bt8_pressed = False

        elif screen == SCREEN_3:
            # Drugi zestaw akcji – wykorzystanie dotąd nieużywanych ruchów

            # ------------------ bt1 -----------------
            if robot.bt1 and not bt1_pressed:
                moves.weird()
                bt1_pressed = True
            elif not robot.bt1 and bt1_pressed:
                bt1_pressed = False

            # ------------------ bt2 -----------------
            if robot.bt2 and not bt2_pressed:
                moves.balerina()
                bt2_pressed = True
            elif not robot.bt2 and bt2_pressed:
                moves.return_to_neutral()
                bt2_pressed = False

            # ------------------ bt3 -----------------
            if robot.bt3 and not bt3_pressed:
                moves.boogie()
                bt3_pressed = True
            elif not robot.bt3 and bt3_pressed:
                bt3_pressed = False

            # ------------------ bt4 -----------------
            if robot.bt4 and not bt4_pressed:
                moves.spin()
                bt4_pressed = True
            elif not robot.bt4 and bt4_pressed:
                bt4_pressed = False
            
            # ------------------ bt5 -----------------
            if robot.bt5 and not bt5_pressed:
                moves.toes()
                bt5_pressed = True
            elif not robot.bt5 and bt5_pressed:
                bt5_pressed = False

            # ------------------ bt6 -----------------
            if robot.bt6 and not bt6_pressed:
                moves.heels()
                bt6_pressed = True
            elif not robot.bt6 and bt6_pressed:
                bt6_pressed = False

            # ------------------ bt7 -----------------
            if robot.bt7 and not bt7_pressed:
                moves.heels_ride()
                bt7_pressed = True  
            elif not robot.bt7 and bt7_pressed:
                bt7_pressed = False

            # ------------------ bt8 -----------------
            if robot.bt8 and not bt8_pressed:
                moves.circles()
                bt8_pressed = True
            elif not robot.bt8 and bt8_pressed:
                bt8_pressed = False

    time.sleep_ms(10)