import pygame
#import numpy as np
import A2S

import time


motory = A2S.A2S()

def init():
    global sound
    
    pygame.mixer.pre_init(40000, channels=2, allowedchanges=1)
    print(pygame.mixer.get_init())
    pygame.init()
    sound = 0
    motory.set_percent(0,0,0,0)   
    sound = pygame.mixer.Sound(motory.signal())
    sound.play(-1)

def nastav(f,a,b,c,d,e):
    global sound
    f(a,b,c,d,e)
    sig = motory.signal()
    if sig[0] != 255:
        sound.stop()
        sound = pygame.mixer.Sound(sig)
        sound.play(-1)

init()

sekvence = [
    (0, 0, 0, 0),
    (50, 50, 50, 50),
    (0, 0, 0, 0),
    (-50, -50, -50, -50),
    (0, 0, 0, 0),
    (0, -50, 0, -50),
    (0, 0, 0, 0),
    (-50, 0, -50, 0),
    (0, 0, 0, 0),
]

while True:
    for hodnoty in sekvence:
        for _ in range(20):
            nastav(motory.set_percent, *hodnoty, 4)
            time.sleep(0.05)