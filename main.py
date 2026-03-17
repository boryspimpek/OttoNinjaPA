import urandom # type: ignore
from servo_lib import RobotConfig, ServoController, NeutralPositions, RobotReceiver
from moves import RobotMoves
import time

cfg    = RobotConfig()
servos = cfg.servos
robot  = cfg.robot

npos = NeutralPositions() # neutral positions

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
sw4_pressed = False

def main():
    global bt1_pressed, bt2_pressed, bt3_pressed, bt4_pressed, bt5_pressed, bt6_pressed, bt7_pressed, bt8_pressed
    global sw3_pressed, sw4_pressed
    
    while True:
        if cfg.tick():
            servos.speed_multiplier = robot.pot1 / 100.0 # ograniczenie prędkości serw 360 stopni

            sw3_pressed = RobotConfig.handle_button(
                robot.sw3,
                sw3_pressed,
                moves.ride_position,
                lambda: servos.move_to_angles(LL, npos.LLN, RL, npos.RLN, step=10, delay=0.02),  # szybki powrót do pozycji neutralnej dla stabilności
            )

            sw4_pressed = RobotConfig.handle_button(
                robot.sw4,
                sw4_pressed,
                moves.ride_position,
                lambda: servos.move_to_angles(LL, npos.LLN, RL, npos.RLN, step=10, delay=0.02),  # szybki powrót do pozycji neutralnej dla stabilności
            )

            if sw3_pressed:
                servos.set_speed(LF, ServoController.map_joystick(robot.ly, npos.JOY_DEAD, npos.LF_SERVO_MIN, npos.LF_SERVO_MAX))
                servos.set_speed(RF, ServoController.map_joystick(-robot.ry, npos.JOY_DEAD, npos.RF_SERVO_MIN, npos.RF_SERVO_MAX))

            if sw4_pressed:
                # Sterowanie rozdzielone (przód/tył, skręt)
                forward = robot.ly
                turn = robot.rx * npos.turn_sensitivity
                servos.set_speed(LF, ServoController.map_joystick(forward + turn, npos.JOY_DEAD, npos.LF_SERVO_MIN, npos.LF_SERVO_MAX))
                servos.set_speed(RF, ServoController.map_joystick(-(forward - turn), npos.JOY_DEAD, npos.RF_SERVO_MIN, npos.RF_SERVO_MAX))

            screen = robot.screen

            if screen == RobotReceiver.SCREEN_2:
                bt1_pressed = RobotConfig.handle_button(robot.bt1, bt1_pressed, moves.steps)
                bt2_pressed = RobotConfig.handle_button(robot.bt2, bt2_pressed, moves.arms)
                bt3_pressed = RobotConfig.handle_button(robot.bt3, bt3_pressed, moves.left_back, moves.return_to_neutral)
                bt4_pressed = RobotConfig.handle_button(robot.bt4, bt4_pressed, moves.left_forward, moves.return_to_neutral)
                bt5_pressed = RobotConfig.handle_button(robot.bt5, bt5_pressed, moves.tilt)
                bt6_pressed = RobotConfig.handle_button(robot.bt6, bt6_pressed, moves.wave)
                bt7_pressed = RobotConfig.handle_button(robot.bt7, bt7_pressed, moves.right_back, moves.return_to_neutral)
                bt8_pressed = RobotConfig.handle_button(robot.bt8, bt8_pressed, moves.right_forward, moves.return_to_neutral)

            elif screen == RobotReceiver.SCREEN_3:
                bt1_pressed = RobotConfig.handle_button(robot.bt1, bt1_pressed, moves.weird)
                bt2_pressed = RobotConfig.handle_button(robot.bt2, bt2_pressed, moves.balerina, moves.return_to_neutral)
                bt3_pressed = RobotConfig.handle_button(robot.bt3, bt3_pressed, moves.boogie)
                bt4_pressed = RobotConfig.handle_button(robot.bt4, bt4_pressed, moves.spin)
                bt5_pressed = RobotConfig.handle_button(robot.bt5, bt5_pressed, moves.toes)
                bt6_pressed = RobotConfig.handle_button(robot.bt6, bt6_pressed, moves.step_left)
                bt7_pressed = RobotConfig.handle_button(robot.bt7, bt7_pressed, moves.step_right)
                bt8_pressed = RobotConfig.handle_button(robot.bt8, bt8_pressed, moves.circles)

        time.sleep_ms(10)
        
if __name__ == "__main__":
    main()