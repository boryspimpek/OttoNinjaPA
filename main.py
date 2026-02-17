import network # type: ignore
import espnow # type: ignore
from servo_lib import RobotReceiver, ServoController
import time

# mapping names to the index in the ServoController list [3, 4, 5, 6, 7, 8]
# Index: 0=GP3, 1=GP4, 2=GP5, 3=GP6, 4=GP7, 5=GP8
RL = 0  # Pin 3
RF = 1  # Pin 4 (360)
RA = 2  # Pin 5
LL = 3  # Pin 6
LF = 4  # Pin 7 (360)
LA = 5  # Pin 8

print("[BOOT] Inicjalizacja serwomechanizmow...")
servos = ServoController([3, 4, 5, 6, 7, 8])
print("[BOOT] ServoController OK")

# --- TRIMS --------------------------------------------------------------
# Serwa 360: podaj o ile trzeba przesunąć żeby stały w miejscu przy speed=0
servos.set_trim_speed(RF, -2)   
servos.set_trim_speed(LF, 0)    

# Serwa zwykłe: podaj o ile stopni odchyla się od oczekiwanego kąta
servos.set_trim_angle(LL, 0)
servos.set_trim_angle(RA, 0)
servos.set_trim_angle(RL, 0)
servos.set_trim_angle(LA, 0)
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
servos.set_speed(LF, 90)  # Stop for 360 servo
servos.set_angle(RA, 90)
servos.set_angle(RL, 120)
servos.set_speed(RF, 90)  # Stop for 360 servo
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
        servos.set_speed(LF, robot.ly)
        servos.set_speed(RF, robot.ry)

        if robot.bt1:
            print("[BTN] bt1")
        if robot.bt2:
            print("[BTN] bt2")
        if robot.bt3:
            print("[BTN] bt3")
        if robot.bt4:
            print("[BTN] bt4")
        if robot.bt5:
            print("[BTN] bt5")
        if robot.bt6:
            print("[BTN] bt6")
        if robot.bt7:
            print("[BTN] bt7")
        if robot.bt8:
            print("[BTN] bt8")
        if robot.sw3:
            print("[SW]  sw3")
        if robot.sw4:
            print("[SW]  sw4")

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