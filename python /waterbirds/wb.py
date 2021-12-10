#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
[waterbirds // 21.12]

always show a screen with two controls: 
    . auto start
        random steps of sound, pneum and both
    . manual state
        sound
        pneumnatics
        sound + pneumatics


log

v01: L + R activation with buttons
v02: two different devices play L+R secuencially

"""

import pygame
import pygame._sdl2 as sdl2
from oscpy.client import OSCClient
from glob import glob
import time

# init
pygame.init()

# this routine show the audio playback devices
debug_mode = False
if (debug_mode):
    is_capture = 0 
    num = sdl2.get_num_audio_devices(is_capture)
    devices = [str(sdl2.get_audio_device_name(i, is_capture), encoding="utf-8") for i in range(num)]
    print("\n".join(devices))



osc_host = "192.168.1.141"
osc_port = 8000
osc_client = []

w = 320
h = 640
window = pygame.display.set_mode((w, h))

colors = [
    (0, 0, 0),          # black
    (242, 232, 207),    # white
    (56, 102, 65),        #   g
    (106, 153, 78),        #   b 
    (167, 201, 87),       #   r
    (188, 71, 73),        #
    ]

# load fonts
font_path = 'RevMiniPixel.ttf'
font = pygame.font.Font(font_path, 20)

# main screen for drawing buttons
draw_canvas = pygame.Surface((w, h))
draw_canvas.fill(colors[0])

# buttons
labels = ["[ A ]: ", "[ B ]: "]
btns = [pygame.draw.rect(draw_canvas, colors[4], pygame.Rect(w/2 - 75, 100+c*200, 150, 150), 2) for c in range(len(labels))]
btns_labels = [font.render(cs, 1, colors[1]) for cs in labels]
btns_states = [False for c in labels]
play_states = [False for c in labels]

# timer events
TIC_EVENT = pygame.USEREVENT + 1
TIC_TIMER = 1000

#states and counters
clock = pygame.time.Clock()

pos = (0,0)
running = True
ii=0

# load sounds
sounds_path = './snds'
snd1 = None
snd2 = None
fns = []


# -osc
def init_osc(oh_ = osc_host, op_ = osc_port):
	global osc_client
	osc_client = OSCClient(oh_, op_)
	return

def update_osc(v = 0):
    global osc_client
    ruta = '/waterbirds/{}'.format(0)
    ruta = ruta.encode()
    osc_client.send_message(ruta, [v])
    print("{}\t{}".format(ruta, v))
    return

# -data stuff
def load_data():
	print ("[DATA]: ok")
	return

# tic for the timer
def tic():
	global ii
	#update_osc(ii)
	#print ("\t\t -->   Aqui ENVIA DATOS")
	ii = ii+1
	return

# keys
def handle_keys(event):
	global running
	if (event.key == pygame.K_q):
		running = False

# handlear eventos con un diccionario
def handle_events():
	event_dict = {
		pygame.QUIT: exit,
		pygame.KEYDOWN: handle_keys,
		TIC_EVENT: tic
		}
	for event in pygame.event.get():
		if event.type in event_dict:
			if (event.type==pygame.KEYDOWN):
				event_dict[event.type](event)
			else:
				event_dict[event.type]()
	return

# handlear clicks del mouse
def handle_mouse_clicks():
    global btns_states, play_states
    # check for mouse pos and click
    pos = pygame.mouse.get_pos()
    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
    # Check collision between buttons and mouse1
    for j,b in enumerate(btns):
        if (b.collidepoint(pos) and pressed1):
            btns_states[j] = not (btns_states[j])
            if (btns_states[j]):
                play_states[j] = btns_states[j]            
                print("[B{}]: ".format(j), btns_states[j])
    return


# update labels and other text in display
def update_text():
	global labels, btns_states
	window.blit(draw_canvas, (0, 0))
    # buttons and labels
	for j, lab in enumerate(btns_labels):
		window.blit(lab, (w/2 - 65, 170+j*200))
		aux_state_label = font.render("{}".format("X" if btns_states[j] else "_"), 1, colors[5])
		window.blit(aux_state_label, (w/2 - 65+50, 170+j*200))
	#other_label = font.render("[step]:  {}".format(ii), 1, colors[2])
	#window.blit(other_label, (370, 690))
	pygame.display.flip()



def init_sound():
    global snd1, snd2, fnsq
    fns = glob(sounds_path+"/*.ogg")
    print (fns)
    #pygame.mixer.pre_init()
    #pygame.mixer.init()
    #snd1 = pygame.mixer.Sound(fns[0])
    #snd2 = pygame.mixer.Sound(fns[1])   
    return


def update_sound():
    if (play_states[0]):
        pygame.mixer.pre_init(devicename="Built-in Audio Analog Stereo")
        pygame.mixer.init()
        time.sleep(1)
        snd1 = pygame.mixer.Sound(fns[0])
        snd2 = pygame.mixer.Sound(fns[1]) 
        pygame.mixer.Sound.play(snd1)
        time.sleep(5)
        pygame.mixer.Sound.play(snd2)
        time.sleep(5)
        pygame.mixer.quit()
        play_states[0] = False

    if (play_states[1]):
        pygame.mixer.pre_init(devicename="Sound BlasterX G1 Analog Stereo")
        pygame.mixer.init()
        time.sleep(1)
        snd1 = pygame.mixer.Sound(fns[0])
        snd2 = pygame.mixer.Sound(fns[1]) 
        pygame.mixer.Sound.play(snd1)
        time.sleep(5)
        pygame.mixer.Sound.play(snd2)
        time.sleep(5)
        pygame.mixer.quit()
        play_states[1] = False
    return



# the loop from outside
def game_loop():
    while running:
        handle_events()
        handle_mouse_clicks()
        update_sound()
        update_text()
        clock.tick(9)

# the main (init+loop)
def main():
    pygame.display.set_caption('[ ~~~~~ ]')
    init_osc()
    init_sound()
    load_data()
    pygame.time.set_timer(TIC_EVENT, TIC_TIMER)
    game_loop()
    print("[-_-] //...")

if __name__=="__main__":
    main()










