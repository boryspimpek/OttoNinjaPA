import network # type: ignore
import espnow # type: ignore
from servo_lib import RobotReceiver, ServoController
import time

# --- KONFIGURACJA PINÓW ---
#                   ESP32-C3 Zero
#                      TOP VIEW
#                ____________________
#               |    USB-C           |
#               |_____________ ______|
#               | [ ] 5V      21 [ ] |
#               | [ ] GND     20 [ ] |
#               | [ ] 3.3v    19 [ ] |
#               | [ ] 0       18 [ ] | 
#               | [ ] 1       10 [ ] | 
#               | [ ] 2        9 [ ] |
#     (RA) CH3  | [ ] 3        8 [ ] | CH7 (LA)
#     (RL) CH2  | [ ] 4        7 [ ] | CH6 (LL)
#     (RF) CH1  | [ ] 5        6 [ ] | CH5 (LF)
#               |____________________|

# Index: 0=GP3, 1=GP4, 2=GP5, 3=GP6, 4=GP7, 5=GP8
RF = 0  # Pin 5 (360)
RL = 1  # Pin 4
RA = 2  # Pin 3
LF = 3  # Pin 6 (360)
LL = 4  # Pin 7
LA = 5  # Pin 8

print("[BOOT] Inicjalizacja serwomechanizmow...")
servos = ServoController([5, 4, 3, 6, 7, 8])
print("[BOOT] ServoController OK")

# --- TRIMS --------------------------------------------------------------
# Serwa 360: podaj o ile trzeba przesunąć żeby stały w miejscu przy speed=0
servos.set_trim_speed(RF, -3)   
servos.set_trim_speed(LF, -3)    

# Serwa zwykłe: podaj o ile stopni odchyla się od oczekiwanego kąta
servos.set_trim_angle(LL, +2)
servos.set_trim_angle(RA, 0)
servos.set_trim_angle(RL, -5)
servos.set_trim_angle(LA, 0)

LF_SERVO_MIN = -16   # pełny tył LF
LF_SERVO_MAX = +16   # pełny przód LF

RF_SERVO_MIN = -13   # pełny tył RF
RF_SERVO_MAX = +13   # pełny przód RF

JOY_DEAD = 3         # strefa martwa
# ------------------------------------------------------------------------

print("[BOOT] Uruchamianie WiFi...")
sta = network.WLAN(network.STA_IF)
sta.active(True)
print("[BOOT] MAC adres:", ':'.join('%02x' % b for b in sta.config('mac')))

print("[BOOT] Uruchamianie ESP-NOW...")
e = espnow.ESPNow()
e.active(True)
robot = RobotReceiver(e)
print("[BOOT] ESP-NOW gotowy, czekam na dane...")

# Set initial neutral positions
servos.set_angle(LL, 60)
servos.set_speed(LF, 0)
servos.set_angle(RA, 90)
servos.set_angle(RL, 120)
servos.set_speed(RF, 0)
servos.set_angle(LA, 90)

print("[BOOT] Serwa ustawione na pozycje startowe")
print("[BOOT] Petla glowna start!")
print("-" * 40)

# Licznik do rzadszego wypisywania statusu
_last_status = 0
_packet_count = 0
_connected = False

while True:
    if robot.update():
        _packet_count += 1

        # Pierwszy pakiet — ogłoś połączenie
        if not _connected:
            _connected = True
            print("[OK] Polaczono! Odebrano pierwszy pakiet.")

        # Co 100 pakietów wypisz aktualny stan joysticków
        if _packet_count % 100 == 0:
            print(f"[STATUS] Pakiety: {_packet_count} | LX:{robot.lx:4d} LY:{robot.ly:4d} RX:{robot.rx:4d} RY:{robot.ry:4d} | POT1:{robot.pot1}")

        # 360 Servos (Continuous Rotation)
        lf_speed = ServoController.map_joystick(robot.ly, JOY_DEAD, LF_SERVO_MIN, LF_SERVO_MAX)
        rf_speed = ServoController.map_joystick(robot.ry, JOY_DEAD, RF_SERVO_MIN, RF_SERVO_MAX)
        servos.set_speed(LF, lf_speed)
        servos.set_speed(RF, rf_speed)

        if robot.bt1:
            print("[BTN] bt1")
            servos.set_angle(RL, 150)  
        if robot.bt2:
            print("[BTN] bt2")
            servos.set_angle(RL, 120)
        if robot.bt3:
            print("[BTN] bt3")
            servos.set_angle(RL, 30)
        if robot.bt4:
            print("[BTN] bt4")
            servos.set_angle(RL, 90)
        if robot.bt5:
            print("[BTN] bt5")
            servos.set_angle(LL, 30)  
        if robot.bt6:
            print("[BTN] bt6")
            servos.set_angle(LL, 60)  
        if robot.bt7:
            print("[BTN] bt7")
            servos.set_angle(LL, 150)  
        if robot.bt8:
            print("[BTN] bt8")
            servos.set_angle(LL, 90)
        if robot.sw3:
            print("[SW]  sw3")
            # servos.set_angle(LL, 0)
            # servos.set_angle(RL, 0)
        if robot.sw4:
            print("[SW]  sw4")
            # servos.set_angle(LL, 180)
            # servos.set_angle(RL, 180)

    else:
        # Brak pakietu — co 3 sekundy przypomnij że czeka
        now = time.ticks_ms()
        if _connected and time.ticks_diff(now, _last_status) > 3000:
            print("[WARN] Brak danych od kontrolera...")
            _last_status = now
        elif not _connected and time.ticks_diff(now, _last_status) > 3000:
            print("[WAIT] Czekam na polaczenie...")
            _last_status = now

    time.sleep_ms(10)