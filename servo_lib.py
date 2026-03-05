import struct
from machine import Pin, PWM # type: ignore

class RobotReceiver:
    def __init__(self, espnow_instance):
        self.e = espnow_instance
        self.lx, self.ly, self.rx, self.ry = 0, 0, 0, 0
        self.pot1 = 0
        self.mask = 0

    def update(self):
        host, msg = self.e.recv(0)
        if msg:
            try:
                self.lx, self.ly, self.rx, self.ry, self.pot1, self.mask = struct.unpack('4bBH', msg)
                return True
            except: pass
        return False

    @property
    def bt1(self): return bool(self.mask & (1 << 0))
    @property
    def bt2(self): return bool(self.mask & (1 << 1))
    @property
    def bt3(self): return bool(self.mask & (1 << 3))
    @property
    def bt4(self): return bool(self.mask & (1 << 2))
    @property
    def bt5(self): return bool(self.mask & (1 << 4))
    @property
    def bt6(self): return bool(self.mask & (1 << 5))
    @property
    def bt7(self): return bool(self.mask & (1 << 6))
    @property
    def bt8(self): return bool(self.mask & (1 << 7))
    @property
    def sw3(self): return bool(self.mask & (1 << 8))
    @property
    def sw4(self): return bool(self.mask & (1 << 9))

class ServoController:
    def __init__(self, pins):
        """pins: lista numerów GPIO, np. [5, 4, 3, 6, 7, 8]"""
        self.servos = []
        for p in pins:
            pwm = PWM(Pin(p), freq=50)
            self.servos.append(pwm)

        self._angle_trims = {}  
        self._speed_trims = {}  

    def set_trim_angle(self, index, delta):
        """Trim dla zwykłego serwa. delta w stopniach, np. set_trim_angle(LL, +3)"""
        self._angle_trims[index] = delta

    def set_trim_speed(self, index, delta):
        """Trim dla serwa 360. delta w jednostkach speed (-100..100), np. set_trim_speed(RF, +4)"""
        self._speed_trims[index] = delta

    def set_angle(self, index, angle):
        """Dla zwykłych serw: 0 do 180 stopni (trim aplikowany automatycznie)"""
        angle = angle + self._angle_trims.get(index, 0)
        angle = max(0, min(180, angle))
        # Standardowe MG90S: 0.5ms (duty ok. 1638) do 2.5ms (duty ok. 8192)
        duty = int(((angle / 180) * (8192 - 1638)) + 1638)
        self.servos[index].duty_u16(duty)

    def set_speed(self, index, speed):
        """Dla serw 360: speed od -100 (tył) do 100 (przód). 0 to stop. (trim aplikowany automatycznie)"""
        speed = speed + self._speed_trims.get(index, 0)
        speed = max(-100, min(100, speed))
        angle = int(((speed + 100) / 200) * 180)
        self.set_angle(index, angle)

    @staticmethod
    def map_joystick(value, joy_dead=3, servo_min=-100, servo_max=100):
        """Mapuje wartość joysticka (-100..+100) na zakres serwa (servo_min..servo_max).

        joy_dead    – strefa martwa wokół zera (domyślnie 3)
        servo_min   – dolny rzeczywisty zakres serwa (np. -16)
        servo_max   – górny rzeczywisty zakres serwa (np. +16)

        Przykład dla LF (zakres -16..+16):
            mapped = ServoController.map_joystick(robot.ly, servo_min=-16, servo_max=16)
        """
        if abs(value) <= joy_dead:
            return 0
        if value > 0:
            return int((value / 100) * servo_max)
        else:
            return int((value / 100) * (-servo_min))