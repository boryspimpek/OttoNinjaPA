import struct
import time
import json
import network  # type: ignore
import espnow   # type: ignore
from machine import Pin, PWM  # type: ignore

# --------------- KONFIGURACJA PINÓW ---------------
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

# Ekrany/tryby zgodne z nadajnikiem FusionPad (mode_robot.py)
SCREEN_MAIN = 0
SCREEN_2 = 1
SCREEN_3 = 2

class RobotReceiver:
    def __init__(self, espnow_instance):
        self.e = espnow_instance
        self.lx, self.ly, self.rx, self.ry = 0, 0, 0, 0
        self.pot1 = 0
        self.screen = 0
        self.mask = 0

    def update(self):
        host, msg = self.e.recv(0)
        if msg:
            try:
                packet_type = msg[0]
                
                if packet_type == 0x01:  # CONTROL packet
                    # struct.pack('B4bBBH', 1, j1x, j1y, j2x, j2y, pot, mode, mask)
                    self.lx, self.ly, self.rx, self.ry, self.pot1, self.screen, self.mask = struct.unpack('B4bBBH', msg)[1:]
                    return 'control'
                
                elif packet_type == 0x02:  # TRIM_SYNC packet
                    # struct.pack('B6b', 2, t0, t1, t2, t3, t4, t5)
                    trim_values = struct.unpack('B6b', msg)[1:]
                    return ('trim_sync', trim_values)
                
                elif packet_type == 0x03:  # SAVE packet
                    # struct.pack('BB', 3, 1)
                    return ('save', msg[1])
                
            except:
                pass
        return None

    @property
    def bt1(self): return bool(self.mask & (1 << 0))
    @property
    def bt2(self): return bool(self.mask & (1 << 1))
    @property
    def bt3(self): return bool(self.mask & (1 << 3)) # intentionally swapped with bt4
    @property
    def bt4(self): return bool(self.mask & (1 << 2)) # intentionally swapped with bt3
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
        self.servos = []
        for p in pins:
            pwm = PWM(Pin(p), freq=50)
            self.servos.append(pwm)
        self._angle_trims = {}
        self._speed_trims = {}
        self._current_angles = {}  # <- śledzenie pozycji
        self.speed_multiplier = 1.0
        self.continuous_servo_indices = []

    def set_trim_angle(self, index, delta):
        self._angle_trims[index] = delta

    def set_trim_speed(self, index, delta):
        self._speed_trims[index] = delta

    def set_angle(self, index, angle):
    # set single angle in degrees
        self._current_angles[index] = angle  # <- zapis pozycji
        angle = angle + self._angle_trims.get(index, 0)
        angle = max(0, min(180, angle))
        duty = int(((angle / 180) * (8192 - 1638)) + 1638)
        self.servos[index].duty_u16(duty)

    def set_angles(self, *args):
    # set multiple angles at once, e.g.:
    # set_angles(i1, angle1, i2, angle2, ...)
        it = iter(args)
        for index, angle in zip(it, it):
            self.set_angle(index, angle)

    def set_speed(self, index, speed):
        # set speed, 0 = stop
        if index in self.continuous_servo_indices:
            speed = speed * self.speed_multiplier

        speed = speed + self._speed_trims.get(index, 0)
        speed = max(-100, min(100, speed))
        angle = int(((speed + 100) / 200) * 180)
        self.set_angle(index, angle)

    def set_speeds(self, *args):
    # set multiple speeds at once, e.g.:
    # set_speeds(i1, speed1, i2, speed2, ...)
        it = iter(args)
        for index, speed in zip(it, it):
            self.set_speed(index, speed)

    def move_to_angles(self, *args, step=2, delay=0.02):
        """Płynny ruch wielu serw jednocześnie.
        move_to_angles(i1, angle1, i2, angle2, ..., step=2, delay=0.02)
        """
        pairs = []
        it = iter(args)
        for index, target in zip(it, it):
            current = self._current_angles.get(index, target)
            pairs.append((index, current, target))

        max_steps = max(int(abs(t - c) / step) for _, c, t in pairs) or 1

        for s in range(max_steps + 1):
            for index, current, target in pairs:
                angle = current + (target - current) * s / max_steps
                self.set_angle(index, int(angle))
            time.sleep(delay)

        # dokładna pozycja końcowa
        for index, _, target in pairs:
            self.set_angle(index, target)

    @staticmethod
    def map_joystick(value, joy_dead=3, servo_min=-100, servo_max=100):
        if abs(value) <= joy_dead:
            return 0
        if value > 0:
            return int((value / 100) * servo_max)
        else:
            return int((value / 100) * (-servo_min))


class RobotConfig:
    # --- Indeksy serw ---
    RF = 0  # Pin 5 (360), right foot
    RL = 1  # Pin 4, right leg
    RA = 2  # Pin 3, right arm
    LF = 3  # Pin 6 (360), left foot
    LL = 4  # Pin 7, left leg
    LA = 5  # Pin 8, left arm

    # --- Zakresy joysticow ---
    JOY_DEAD     = 3
    LF_SERVO_MIN = -16
    LF_SERVO_MAX = +15
    RF_SERVO_MIN = -16
    RF_SERVO_MAX = +16

    def __init__(self):
        print("[BOOT] Inicjalizacja serwomechanizmow...")
        self.servos = ServoController([5, 4, 3, 6, 7, 8])
        self.servos.continuous_servo_indices = [self.RF, self.LF]
        print("[BOOT] ServoController OK")

        # Wczytaj konfigurację z pliku JSON
        self.load_from_json()

        print("[BOOT] Uruchamianie WiFi...")
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        print("[BOOT] MAC adres:", ':'.join('%02x' % b for b in sta.config('mac')))

        print("[BOOT] Uruchamianie ESP-NOW...")
        e = espnow.ESPNow()
        e.active(True)
        self.robot = RobotReceiver(e)
        print("[BOOT] ESP-NOW gotowy, czekam na dane...")

        self.servos.set_speed(self.LF,   0)
        self.servos.set_angle(self.LL,  60)
        self.servos.set_angle(self.LA,  90)
        self.servos.set_speed(self.RF,   0)
        self.servos.set_angle(self.RL, 120)
        self.servos.set_angle(self.RA,  90)

        print("[BOOT] Serwa ustawione na pozycje startowe")
        print("[BOOT] Petla glowna start!")
        print("-" * 40)

        self._connected     = False
        self._packet_count  = 0
        self._last_warn     = 0
        self._last_packet   = time.ticks_ms()

    def _apply_combined_trims(self, offset_trims):
        # Sumujemy bazę z pliku z tym, co aktualnie przysłano w pakiecie
        combined = [b + o for b, o in zip(self.base_trims, offset_trims)]
        
        # Przekazujemy zsumowane wartości do sterownika serw
        self.servos.set_trim_speed(self.RF, combined[0])
        self.servos.set_trim_angle(self.RL, combined[1])
        self.servos.set_trim_angle(self.RA, combined[2])
        self.servos.set_trim_speed(self.LF, combined[3])
        self.servos.set_trim_angle(self.LL, combined[4])
        self.servos.set_trim_angle(self.LA, combined[5])
        
    def load_from_json(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                # Zapisujemy to jako naszą BAZĘ, której nie zmieniamy pakietami trim
                self.base_trims = config.get('servo_trims', [0, 0, 0, 0, 0, 0])
                print(f"[CONFIG] Baza wczytana: {self.base_trims}")
        except:
            self.base_trims = [-3, -8, 0, -3, 2, 0] # Twoje domyślne
        
        # Na starcie aplikujemy bazę jako aktualne trimy
        self._apply_combined_trims([0, 0, 0, 0, 0, 0])

    def save_to_json(self):
        """Zapisuje AKTUALNE (zsumowane) wartości trimów do pliku i aktualizuje bazę"""
        try:
            # 1. Pobieramy zsumowane wartości, które są obecnie w kontrolerze serw
            new_total_trims = [
                self.servos._speed_trims.get(self.RF, 0),
                self.servos._angle_trims.get(self.RL, 0),
                self.servos._angle_trims.get(self.RA, 0),
                self.servos._speed_trims.get(self.LF, 0),
                self.servos._angle_trims.get(self.LL, 0),
                self.servos._angle_trims.get(self.LA, 0)
            ]
            
            config = {'servo_trims': new_total_trims}
            
            with open('config.json', 'w') as f:
                json.dump(config, f)
            
            # --- KLUCZOWA POPRAWKA ---
            # Nowa suma staje się nową bazą w pamięci robota
            self.base_trims = new_total_trims
            # -------------------------
            
            print(f"[SAVE] Nowa baza zapisana i ustawiona: {self.base_trims}")
            return True
        except Exception as e:
            print(f"[SAVE] Błąd: {e}")
            return False

    def handle_trim_sync(self, trim_values):
        # 1. Oblicz i zaaplikuj sumę (Baza z JSON + Offset z Pilota)
        self._apply_combined_trims(trim_values)
        
        # 2. Wymuś ruch do pozycji "neutralnych" 
        # Dzięki temu widzisz efekt trimowania na żywo!
        
        # Serwa 360 (stopy) - ustawiamy speed na 0 (czyli 90 stopni + trim)
        self.servos.set_speed(self.RF, 0)
        self.servos.set_speed(self.LF, 0)
        
        # Serwa kątowe - ustawiamy ich domyślne kąty "stania"
        self.servos.set_angle(self.RL, 120)
        self.servos.set_angle(self.LL, 60)
        self.servos.set_angle(self.RA, 90)
        self.servos.set_angle(self.LA, 90)
        
        print(f"[TRIM LIVE] Offset: {trim_values}")

    def handle_save_command(self):
        """Obsługa pakietu SAVE - zapisuje konfigurację"""
        if self.save_to_json():
            print("[SAVE] Konfiguracja zapisana pomyślnie")
        else:
            print("[SAVE] Błąd zapisu konfiguracji")

    def tick(self):
        """Wywołaj raz na początku pętli while.
        Zwraca True jeśli przyszedł nowy pakiet — wtedy możesz czytać robot.bt*, robot.lx itp.
        Zwraca False jeśli brak pakietu (komunikaty o braku połączenia drukowane automatycznie).
        """
        now = time.ticks_ms()

        result = self.robot.update()
        if result:
            self._packet_count += 1
            self._last_packet = now

            if not self._connected:
                self._connected = True
                print("[OK] Polaczono! Odebrano pierwszy pakiet.")

            # Obsługa różnych typów pakietów
            if result == 'control':
                # Standardowy pakiet sterowania - nic specjalnego nie robimy
                pass
            elif result[0] == 'trim_sync':
                # Pakiet synchronizacji trimów
                self.handle_trim_sync(result[1])
            elif result[0] == 'save':
                # Pakiet zapisu konfiguracji
                if result[1] == 1:
                    self.handle_save_command()

            if self._packet_count % 100 == 0 and result == 'control':
                r = self.robot
                print(f"[STATUS] Pakiety: {self._packet_count} | "
                      f"LX:{r.lx:4d} LY:{r.ly:4d} RX:{r.rx:4d} RY:{r.ry:4d} | POT1:{r.pot1}")
            return True

        else:
            # Komunikaty tylko, jeśli NAPRAWDĘ długo nie było nowych pakietów
            if time.ticks_diff(now, self._last_packet) > 3000 and time.ticks_diff(now, self._last_warn) > 3000:
                if self._connected:
                    print("[WARN] Brak danych od kontrolera...")
                else:
                    print("[WAIT] Czekam na polaczenie...")
                self._last_warn = now
            return False
