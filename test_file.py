#############################################
from servo_lib import RobotConfig
cfg = RobotConfig()
servos = cfg.servos
LL = cfg.LL
RL = cfg.RL

servos.move_to_angles(LL, 60, RL, 120)

servos.move_to_angles(LL, 150, RL, 30, step=10, delay=0.02)

