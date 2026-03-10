import time
import urandom # type: ignore

class RobotMoves:
    def __init__(self, servos, LF, RF, LL, RL, LA, RA):
        self.servos = servos
        self.LF = LF
        self.RF = RF
        self.LL = LL
        self.RL = RL
        self.LA = LA
        self.RA = RA

    def return_to_neutral(self):
        self.servos.set_speeds(self.LF, 0, self.RF, 0)
        self.servos.move_to_angles(self.LL, 60, self.RL, 120)
        self.servos.move_to_angles(self.LA, 90, self.RA, 90)

    def tilt_right(self):
        self.servos.move_to_angles(self.LL, 10, self.RL, 86)
        time.sleep(0.05)

    def tilt_left(self):
        self.servos.move_to_angles(self.LL, 90, self.RL, 170)
        time.sleep(0.05)

    def ride_position(self):
        self.servos.move_to_angles(self.LL, 150, self.RL, 30, step=10, delay=0.02)
        time.sleep(0.5)

    def left_leg_swing_forward(self):
        self.tilt_right()
        self.servos.set_speed(self.RF, -5)

    def right_leg_swing_forward(self):
        self.tilt_left()
        self.servos.set_speed(self.LF, 5)

    def left_leg_swing_back(self):
        self.tilt_right()
        self.servos.set_speed(self.RF, 5)

    def right_leg_swing_back(self):
        self.tilt_left()
        self.servos.set_speed(self.LF, -5)

    def wave(self, delay=0.1):
        self.tilt_right()
        self.servos.move_to_angles(self.LL, 60, step=5, delay=0.02)
        time.sleep(delay)
        self.servos.move_to_angles(self.LL, 20, step=5, delay=0.02)
        time.sleep(delay)
        self.tilt_left()
        self.servos.move_to_angles(self.RL, 120, step=5, delay=0.02)
        time.sleep(delay)
        self.servos.move_to_angles(self.RL, 160, step=5, delay=0.02)
        time.sleep(delay)
        self.return_to_neutral()

    def steps(self, delay=0.1):
        for i in range(3):
            self.servos.move_to_angles(self.LL, 80, self.RL, 170)
            time.sleep(delay)
            self.servos.move_to_angles(self.LL, 10, self.RL, 100)
            time.sleep(delay)
        self.return_to_neutral()

    def tilt(self, delay=0.1):
        for i in range(3):
            self.servos.move_to_angles(self.LL, 85, self.RL, 140)
            time.sleep(delay)
            self.servos.move_to_angles(self.LL, 40, self.RL, 95)
            time.sleep(delay)
        self.return_to_neutral()

    def weird(self, iterations=3):
        for _ in range(iterations):
            lf_speed = urandom.randint(5, 10) if urandom.randint(0, 1) else urandom.randint(-10, -5)
            rf_speed = urandom.randint(5, 10) if urandom.randint(0, 1) else urandom.randint(-10, -5)
            self.servos.set_speeds(self.LF, lf_speed, self.RF, rf_speed)
            time.sleep(1)
        self.return_to_neutral()

    def arms(self):
        for i in range(3):
            self.servos.move_to_angles(self.LA, 60, self.RA, 60)
            time.sleep(0.1)
            self.servos.move_to_angles(self.LA, 120, self.RA, 120)
            time.sleep(0.1)
        self.return_to_neutral()