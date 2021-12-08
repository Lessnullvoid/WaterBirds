import random
from pygame import mixer
import time
from pathlib import Path


data_folder = Path('/Users/microhm/Desktop/01_Proyectos_proceso/Tania_Waterbirds/Waterbirds/')

_songs = ['0027_WanderingWhistlingDuck2_flockinflight_01.ogg', '0026_WanderingWhistlingDuck1_singlebird_01.ogg', '0025_MagpieGoose1flock_01.ogg']
_currently_playing_song = None

def play_a_different_song():
    global _currently_playing_song, _songs
    next_song = random.choice(_songs)
    while next_song == _currently_playing_song:
        next_song = random.choice(_songs)
    _currently_playing_song = next_song
    pygame.mixer.init()
    pygame.mixer.music.load(next_song)
    pygame.mixer.music.play()
