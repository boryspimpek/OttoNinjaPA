"""
servo_calib.py — interaktywny kalibratory serw LL i RL przez REPL
=================================================================
Sterowanie:
  a / d  — RL  lewo/prawo (−1 / +1 stopień)
  j / l  — LL  lewo/prawo (−1 / +1 stopień)
  A / D  — RL  skok −10 / +10 stopni  (Shift+a / Shift+d)
  J / L  — LL  skok −10 / +10 stopni  (Shift+j / Shift+l)
  r      — reset obu serw do 90°
  p      — wypisz aktualne pozycje
  q      — wyjście (serwa zostają na ostatniej pozycji)

Użycie:
  >>> import servo_calib
  >>> servo_calib.run()
"""

import sys
import select
from machine import Pin, PWM  # type: ignore

# ── Piny (zgodnie z servo_lib.py) ──────────────────────────────────────
PIN_RL = 4   # RL = index 1 → pin 4
PIN_LL = 7   # LL = index 4 → pin 7

TRIM_RL = -5  # trim z RobotConfig
TRIM_LL = +2  # trim z RobotConfig

# ── PWM helpers ────────────────────────────────────────────────────────
def _make_pwm(pin_no):
    return PWM(Pin(pin_no), freq=50)

def _angle_to_duty(angle):
    angle = max(0, min(180, angle))
    return int(((angle / 180) * (8192 - 1638)) + 1638)

def _set_angle_raw(pwm, angle):
    pwm.duty_u16(_angle_to_duty(angle))

def _set_angle(pwm, logical_angle, trim):
    """Ustawia kąt z trymem — dokładnie jak ServoController.set_angle()"""
    _set_angle_raw(pwm, logical_angle + trim)

# ── Główna pętla ────────────────────────────────────────────────────────
def run(start_ll=60, start_rl=120):

    pwm_rf = PWM(Pin(5), freq=50)
    pwm_lf = PWM(Pin(6), freq=50)
    _set_angle_raw(pwm_rf, 90-3)  # 90° = stop dla serwa 360
    _set_angle_raw(pwm_lf, 90-3)

    pwm_rl = _make_pwm(PIN_RL)
    pwm_ll = _make_pwm(PIN_LL)

    pos_rl = start_rl
    pos_ll = start_ll

    _set_angle(pwm_rl, pos_rl, TRIM_RL)
    _set_angle(pwm_ll, pos_ll, TRIM_LL)

    print("=== KALIBRACJA SERW ===")
    print(f"RL (pin {PIN_RL}, trim {TRIM_RL:+d}):  a/d = ±1°,  A/D = ±10°")
    print(f"LL (pin {PIN_LL}, trim {TRIM_LL:+d}):  j/l = ±1°,  J/L = ±10°")
    print("r = reset do 90° | p = pokaż pozycje | q = wyjście")
    print(f"Start: RL={pos_rl}°  LL={pos_ll}°")
    print("-" * 40)

    KEYMAP = {
        'a': ('rl', -1),  'd': ('rl', +1),
        'A': ('rl', -10), 'D': ('rl', +10),
        'j': ('ll', -1),  'l': ('ll', +1),
        'J': ('ll', -10), 'L': ('ll', +10),
    }

    while True:
        # Czytaj znak bez blokowania (działa w MicroPython REPL)
        if sys.stdin in select.select([sys.stdin], [], [], 0.05)[0]:
            ch = sys.stdin.read(1)
        else:
            continue

        if ch == 'q':
            print(f"[EXIT] RL={pos_rl}°  LL={pos_ll}°")
            pwm_rl.deinit()
            pwm_ll.deinit()
            pwm_rf.deinit()
            pwm_lf.deinit()
            break

        elif ch == 'r':
            pos_rl = 120
            pos_ll = 60
            _set_angle(pwm_rl, pos_rl, TRIM_RL)
            _set_angle(pwm_ll, pos_ll, TRIM_LL)
            print(f"[RESET] RL=120°  LL=60°")

        elif ch == 'p':
            print(f"[POS]  RL={pos_rl}°  LL={pos_ll}°")

        elif ch in KEYMAP:
            servo, delta = KEYMAP[ch]
            if servo == 'rl':
                pos_rl = max(0, min(180, pos_rl + delta))
                _set_angle(pwm_rl, pos_rl, TRIM_RL)
                print(f"  RL = {pos_rl:3d}°")
            else:
                pos_ll = max(0, min(180, pos_ll + delta))
                _set_angle(pwm_ll, pos_ll, TRIM_LL)
                print(f"  LL = {pos_ll:3d}°")