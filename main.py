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


def handle_button(current_state, was_pressed, on_press, on_release=None):
    if current_state and not was_pressed:
        on_press()
        return True
    if not current_state and was_pressed:
        if on_release is not None:
            on_release()
        return False
    return was_pressed


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
        # Aktualizacja ogranicznika prędkości z potencjometru (0-100 -> 0.0-1.0)
        servos.speed_multiplier = robot.pot1 / 100.0

        sw3_pressed = handle_button(
            robot.sw3,
            sw3_pressed,
            moves.ride_position,
            lambda: servos.move_to_angles(LL, 60, RL, 120, step=10, delay=0.02),  # powrót do pozycji neutralnej
        )

        if sw3_pressed:
            servos.set_speed(LF, ServoController.map_joystick(robot.ly, cfg.JOY_DEAD, cfg.LF_SERVO_MIN, cfg.LF_SERVO_MAX))
            servos.set_speed(RF, ServoController.map_joystick(-robot.ry, cfg.JOY_DEAD, cfg.RF_SERVO_MIN, cfg.RF_SERVO_MAX))

        screen = robot.screen

        if screen == SCREEN_2:
            bt1_pressed = handle_button(robot.bt1, bt1_pressed, moves.steps)

            bt2_pressed = handle_button(robot.bt2, bt2_pressed, moves.arms)

            bt7_pressed = handle_button(robot.bt7, bt7_pressed, moves.right_back, moves.return_to_neutral)

            bt8_pressed = handle_button(robot.bt8, bt8_pressed, moves.right_forward, moves.return_to_neutral)

            bt5_pressed = handle_button(robot.bt5, bt5_pressed, moves.tilt)

            bt6_pressed = handle_button(robot.bt6, bt6_pressed, moves.wave)

            bt3_pressed = handle_button(robot.bt3, bt3_pressed, moves.left_back, moves.return_to_neutral)

            bt4_pressed = handle_button(robot.bt4, bt4_pressed, moves.left_forward, moves.return_to_neutral)

        elif screen == SCREEN_3:
            # Drugi zestaw akcji – wykorzystanie dotąd nieużywanych ruchów

            bt1_pressed = handle_button(robot.bt1, bt1_pressed, moves.weird)

            bt2_pressed = handle_button(robot.bt2, bt2_pressed, moves.balerina, moves.return_to_neutral)

            bt3_pressed = handle_button(robot.bt3, bt3_pressed, moves.boogie)

            bt4_pressed = handle_button(robot.bt4, bt4_pressed, moves.spin)

            bt5_pressed = handle_button(robot.bt5, bt5_pressed, moves.toes)

            bt6_pressed = handle_button(robot.bt6, bt6_pressed, moves.step_left)

            bt7_pressed = handle_button(robot.bt7, bt7_pressed, moves.step_right)

            bt8_pressed = handle_button(robot.bt8, bt8_pressed, moves.circles)

    time.sleep_ms(10)
