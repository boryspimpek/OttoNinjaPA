from servo_lib import RobotConfig, ServoController
import time

cfg    = RobotConfig()
servos = cfg.servos
robot  = cfg.robot

RF, RL, RA = cfg.RF, cfg.RL, cfg.RA
LF, LL, LA = cfg.LF, cfg.LL, cfg.LA

while True:
    if cfg.tick():
        # --- Joysticki ---
        servos.set_speed(LF, ServoController.map_joystick(robot.ly, cfg.JOY_DEAD, cfg.LF_SERVO_MIN, cfg.LF_SERVO_MAX))
        servos.set_speed(RF, ServoController.map_joystick(-robot.ry, cfg.JOY_DEAD, cfg.RF_SERVO_MIN, cfg.RF_SERVO_MAX))

        # --- Przyciski ---
        if robot.bt1: servos.set_angle(RL, 150)
        if robot.bt2: servos.set_angle(RL, 120)
        if robot.bt3: servos.set_angle(RL,  30)
        if robot.bt4: servos.set_angle(RL,  90)
        if robot.bt5: servos.set_angle(LL,  30)
        if robot.bt6: servos.set_angle(LL,  60)
        if robot.bt7: servos.set_angle(LL, 150)
        if robot.bt8: servos.set_angle(LL,  90)

    time.sleep_ms(10)