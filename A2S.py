import numpy as np
import pygame

# -----------------------------
# A2S: knihovna na generaci signálu pro servo  pomocí audia
# -----------------------------

class A2S:
    def __init__(self, frequency=160, sample_rate=40000):
        
        self.frequency = frequency
        self.sample_rate = sample_rate
        self.duration = 1 / frequency

        # buffer size
        self.buffer_size = int(self.sample_rate * self.duration)
        self.signalLR = np.int16(np.zeros((self.buffer_size * 2)))

        # coefficients
        self.servo_koef = np.array([[0, 100],
                                    [0, 100],
                                    [0, 100],
                                    [0, 100]])

        self.servo_prom = np.array([[0, 1, 0, 0],
                                    [0, 1, 0, 0],
                                    [0, 1, 0, 0],
                                    [0, 1, 0, 0]])

        self.servo_sig = np.int16(np.zeros((4, 2, 40)))

        self._generate_servo_signals()
        #self._init_audio(
    def signal(self):
        return self.signalLR.tobytes()
    # -----------------------------
    # pomocná funkce pro generování signálu
    # -----------------------------
    def _generate_servo_signals(self):
        for i in range(4):
            self.servo_prom[i, 3] = np.int16(32767 * (self.servo_koef[i, 1] / 100))

        for i in range(20):
            for j in range(4):
                sign = 1 if j % 2 == 0 else -1
                self.servo_sig[j, 0, i] = sign * np.int16((3276 * (((1 / np.sin((np.pi / 2) + (np.pi / (2 * 21)) * (i))) ** 0.5))) - 3276)
                self.servo_sig[j, 0, i + 20] = sign * np.int16(29491 + (3276 * ((np.sin((np.pi / (2 * 21)) * (i))) ** 0.5)))

                self.servo_sig[j, 1, i] = sign * np.int16(29491 + (3276 * ((np.sin((np.pi / (2 * 21)) * (19 - i))) ** 0.5)))
                self.servo_sig[j, 1, i + 20] = sign * np.int16((3276 * (((1 / np.sin((np.pi / 2) + (np.pi / (2 * 21)) * (19 - i))) ** 0.5))) - 3276)

    # -----------------------------
    # inicializace pygame audia
    # -----------------------------
    #def _init_audio(self):
        
       
        

    # -----------------------------
    # aktualizace signálu
    # -----------------------------
    def set_motors(self, m0=0, m1=0, m2=0, m3=0, delta=1):
        self.servo_prom[0, 0], self.servo_prom[1, 0], self.servo_prom[2, 0], self.servo_prom[3, 0] = m0, m1, m2, m3

        #self.servo_prom[:, 0] = np.clip(((self.servo_prom[:, 0] + self.servo_koef[:, 0]) / 5).astype(int), -20, 20)

        if np.any(self.servo_prom[:, 0] != self.servo_prom[:, 1]):
            self.servo_prom[:, 0] = np.clip(self.servo_prom[:, 0], self.servo_prom[:, 1] - delta, self.servo_prom[:, 1] + delta)
            self.servo_prom[:, 2] = (80 + self.servo_prom[:, 0]).astype(int)

            # channel 0
            self.signalLR[0:80:2] = self.servo_sig[0, 0]
            self.signalLR[80:(2 * self.servo_prom[0, 2]):2] = 32767
            self.signalLR[(2 * self.servo_prom[0, 2]):(80 + 2 * self.servo_prom[0, 2]):2] = self.servo_sig[0, 1]
            self.signalLR[(80 + 2 * self.servo_prom[0, 2]):self.buffer_size:2] = 0

            # channel 1
            start = self.buffer_size
            self.signalLR[start:(start + 80):2] = self.servo_sig[1, 0]
            self.signalLR[(start + 80):(start + 2 * self.servo_prom[1, 2]):2] = -32767
            self.signalLR[(start + 2 * self.servo_prom[1, 2]):(start + 80 + 2 * self.servo_prom[1, 2]):2] = self.servo_sig[1, 1]
            self.signalLR[(start + 80 + 2 * self.servo_prom[1, 2])::2] = 0

            # channel 2
            self.signalLR[1:81:2] = self.servo_sig[2, 0]
            self.signalLR[81:(1 + 2 * self.servo_prom[2, 2]):2] = 32767
            self.signalLR[(1 + 2 * self.servo_prom[2, 2]):(81 + 2 * self.servo_prom[2, 2]):2] = self.servo_sig[2, 1]
            self.signalLR[(81 + 2 * self.servo_prom[2, 2]):self.buffer_size + 1:2] = 0

            # channel 3
            self.signalLR[start + 1:(start + 81):2] = self.servo_sig[3, 0]
            self.signalLR[(start + 81):(1 + start + 2 * self.servo_prom[3, 2]):2] = -32767
            self.signalLR[(1 + start + 2 * self.servo_prom[3, 2]):(81 + start + 2 * self.servo_prom[3, 2]):2] = self.servo_sig[3, 1]
            self.signalLR[(81 + start + 2 * self.servo_prom[3, 2])::2] = 0


            self.servo_prom[:, 1] = self.servo_prom[:, 0]
        else:
            self.signalLR[0] = 255
            

    # -----------------------------
    # přímé řízení motorů
    # -----------------------------
    def set_percent(self, s0=0, s1=0, s2=0, s3=0, delta=1):
        """vstupní rozsah: 0–100"""
        vals = [np.clip(v, -100, 100) for v in (s0, s1, s2, s3)]
        scaled = [int((v - 100) * 0.2) for v in vals]  # map to approx -20..20
        scaled.append(delta)
        self.set_motors(*scaled)

    def set_angle_90(self, s0=0, s1=0, s2=0, s3=0, delta=1):
        """vstupní rozsah: -90 – +90"""
        vals = [np.clip(v, -90, 90) for v in (s0, s1, s2, s3)]
        scaled = [int(v * (20/90)) for v in vals]
        scaled.append(delta)
        self.set_motors(*scaled)

    def set_angle_180(self, s0=0, s1=0, s2=0, s3=0, delta=1):
        """vstupní rozsah: 0 – 180"""
        vals = [np.clip(v, 0, 180) for v in (s0, s1, s2, s3)]
        scaled = [int(((v - 90) * (20/90))) for v in vals]
        scaled.append(delta)
        self.set_motors(*scaled)