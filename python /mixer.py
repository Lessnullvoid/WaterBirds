from pygame import mixer
import time

mixer.init()
mixer.music.load('/Users/microhm/Desktop/01_Proyectos_proceso/Tania_Waterbirds/Waterbirds/0026_WanderingWhistlingDuck1_singlebird_01.ogg')
mixer.music.play()
time.sleep(5)
mixer.music.stop()
