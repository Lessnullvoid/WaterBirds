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
v03: file sequence randomly playing across channels
v04: steady mode, osc comms, serial comms

"""

import pygame
import pygame._sdl2 as sdl2
from oscpy.client import OSCClient
from glob import glob
import time, random
import argparse

args = None
mode = "master"
osc_client_a = None
osc_client_b = None

colors = [
    (24, 48, 48),   # Medium Jungle Green
    (216, 168, 96), # Streusel Cake
    (216, 96, 48),  # Tangerine Bliss
    (24, 96, 96),   # Emerald Pool
    (0, 48, 48),    # Daintree
    (212, 64, 38)   #more tanger
    ]

# pos and states
w = 320
h = 640
pos = (0,0)
ii = 0
running = True

dtrack_a = None
dtrack_b = None
is_playing_a = False
is_playing_b = False
rdelay = 0

in_auto = False
in_manual = False
state = 0
# s0: select, 
# s1: auto,
# s2: manual+menu, 
# s3: manual+sound, 
# s4: manual+pneum, 
# s5: manual both

# init
pygame.init()
window = pygame.display.set_mode((w, h))

# load fonts
font_path = 'RevMiniPixel.ttf'
font = pygame.font.Font(font_path, 20)

# main screen for drawing buttons
select_canvas = pygame.Surface((w, h))
select_canvas.fill(colors[0])
manual_canvas = pygame.Surface((w, h))
manual_canvas.fill(colors[3])
running_canvas = pygame.Surface((w, h))
running_canvas.fill(colors[5])

# buttons
labels_select = ["[  AUTO  ]", "[ MANUAL ]"]
btns_select = [pygame.draw.rect(select_canvas, colors[3], pygame.Rect(w/2 - 125, 80+c*240, 250, 200), 2) for c in range(len(labels_select))]
btns_select_labels = [font.render(label, 1, colors[1]) for label in labels_select]

labels_manual = ["[  SPEAKERS  ]", "[PNEUMATICS]", "[     BOTH     ]"]
btns_manual = [pygame.draw.rect(manual_canvas, colors[4], pygame.Rect(w/2 - 125, 70+c*155, 250, 140), 2) for c in range(len(labels_manual))]
btns_manual_labels = [font.render(label, 1, colors[1]) for label in labels_manual]

labels_running = ["+ RUNNING +","[   STOP   ]"]
btns_running = [pygame.draw.rect(running_canvas, colors[1], pygame.Rect(w/2 - 125, 80+c*240, 250, 200), 2) for c in range(len(labels_running))]
btns_running_labels = [font.render(label, 1, colors[0]) for label in labels_running]

# timer events
TIC_EVENT = pygame.USEREVENT + 1
TIC_TIMER = 1000
clock = pygame.time.Clock()

# sounds alloc
sounds_path = './ogg'
sndA = None
sndB = None
fns = []
current_dev = None
t0a = 0
t0b = 0
i_a = 0
i_b = 0

# names of the devices
device_a = "Built-in Audio Analog Stereo"
device_b = "Audio Adapter (Planet UP-100, Genius G-Talk) Analog Stereo"
#device_b = "Sound BlasterX G1 Analog Stereo"

def show_devices():
    # show the audio playback devices
    is_capture = 0 
    num = sdl2.get_num_audio_devices(is_capture)
    devices = [str(sdl2.get_audio_device_name(i, is_capture), encoding="utf-8") for i in range(num)]
    print("\n".join(devices))
    return

# -osc
def init_osc(oha_ = "192.168.1.136", opa_ = "9105", ohb_ = "192.168.1.250", opb_ = "9106", ):
	global osc_client_a, osc_client_b
	osc_client_a = OSCClient(oha_, opa_)
	osc_client_b = OSCClient(ohb_, opb_)
	return

def update_osc(va = 0, vb = 0):
    global osc_client_a, osc_client_b
    ruta = '/waterbirds/test/{}'.format(0)
    ruta = ruta.encode()
    osc_client_a.send_message(ruta, [va])
    osc_client_b.send_message(ruta, [vb])
    print("{}\t{}".format(ruta, va))
    print("{}\t{}".format(ruta, vb))
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
    global state, in_auto, in_manual
    # check for mouse pos and click
    pos = pygame.mouse.get_pos()
    pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()
    # buttons and mouse
    if state==0: 
        for j,b in enumerate(btns_select):
            if (b.collidepoint(pos) and pressed1):
                #has btn[1] been pressed?
                if (j==0 and not (in_auto or in_manual)):
                    in_auto = True
                    state = 1
                    print("\n\n[B{}]: ~AUTO~ mode -------------".format(j))
                    time.sleep(0.2)
                elif (j==1 and not (in_auto or in_manual)):
                    in_manual = True
                    state = 2
                    print("\n\n[B{}]: ~MANUAL~ mode -----------".format(j))
                    time.sleep(0.2)
    elif state==1:
        for j,b in enumerate(btns_running):
            if (b.collidepoint(pos) and pressed1):
                if(j==1 and in_auto):
                    in_auto = False
                    state = 0
                    print("[B{}]: -------------- ~AUTO~ stopped\n\n".format(j))
                    time.sleep(0.2)
    elif state==2: 
        for j,b in enumerate(btns_manual):
            if (b.collidepoint(pos) and pressed1):
                if(j==0 and in_manual):
                    state = 3
                    print("[B{}]: ~MANUAL SOUND ONLY ".format(j))
                    time.sleep(0.2)
                elif(j==1 and in_manual):
                    state = 4
                    print("[B{}]: ~MANUAL PNEUM ONLY ".format(j))
                    time.sleep(0.2)
                elif(j==2 and in_manual):
                    state = 5
                    print("[B{}]: ~MANUAL BOTH ".format(j))
                    time.sleep(0.2)
    elif state==3 or state==4 or state==5:
        for j,b in enumerate(btns_running):
            if (b.collidepoint(pos) and pressed1):
                if(j==1 and in_manual):
                    in_manual = False
                    state = 0
                    print("[B{}]: -------------- ~MANUAL~ stopped\n\n".format(j))
                    time.sleep(0.2)
    return
# s0: select, 
# s1: auto,
# s2: manual+menu, 
# s3: manual+sound, 
# s4: manual+pneum, 
# s5: manual both

# update labels and other text in display
def update_text():
    global labels_select, btns_select_states
    if state==0:
        window.blit(select_canvas, (0, 0))
        for j, lab in enumerate(btns_select_labels):
            window.blit(lab, (w/2 - 55, 170+j*240))
    if state==1:
        window.blit(running_canvas, (0, 0))
        for j, lab in enumerate(btns_running_labels):
            window.blit(lab, (w/2 - 55, 170+j*240))
    if state==2:
        window.blit(manual_canvas, (0, 0))
        for j, lab in enumerate(btns_manual_labels):
            window.blit(lab, (w/2 - 65, 140+j*155))
    if state==3 or state==4 or state==5:
        window.blit(running_canvas, (0, 0))
        for j, lab in enumerate(btns_running_labels):
            window.blit(lab, (w/2 - 55, 170+j*240))
    pygame.display.flip()



def init_sound():
    global fns, t0a, t0b, delay_btwn, dtrack_a, dtrack_b, rdelay
    fns = glob(sounds_path+"/*.ogg")
    fns.sort()
    print ("\n".join(fns))
    # play_timers reference
    t0a = 0
    t0b = 0
    delay_btwn = 10
    rdelay = 1
    dtrack_a = 0
    dtrack_b = 0
    #pygame.mixer.pre_init()
    #pygame.mixer.init()
    #snd1 = pygame.mixer.Sound(fns[0])
    #snd2 = pygame.mixer.Sound(fns[1])   
    return


def manage_sound():
    # updates timers for playing and manage manual/auto
    global sndA, sndB, fns, lenA, lenB, t0a, t0b, rdelay, dtrack_a, dtrack_b, is_playing_a, is_playing_b, i_a, i_b, current_dev
    now = time.perf_counter()
    if in_auto:
        # start_playing_a
        if ( (not is_playing_a) and (not is_playing_b) and ( (now - (t0a)) > (dtrack_a + delay_btwn + rdelay) ) ):
            if (random.randint(0,1)==0): 
                pygame.mixer.pre_init(devicename = device_a)
                current_dev = device_a
                print("̣\t[>>] {}".format(device_a))
            elif (random.randint(0,1)==1): 
                pygame.mixer.pre_init(devicename = device_b)
                current_dev = device_b
                print("̣\t[>>] {}".format(device_b))
            # init the mixer
            pygame.mixer.init()
            # random variation of delay
            rdelay = random.random() * delay_btwn
            # index of audio file
            i_a = random.randint(0,len(fns)-1)
            sndA = pygame.mixer.Sound(fns[i_a])
            i_b = random.randint(0,len(fns)-1)
            sndB = pygame.mixer.Sound(fns[i_b])
            # duration of track
            dtrack_a = sndA.get_length()
            dtrack_b = sndB.get_length()
            # start playing a
            print("\t[_>>] A {} :: {} :: {} secs".format(time.ctime(), fns[i_a], dtrack_a))
            pygame.mixer.Sound.play(sndA)
            t0a = time.perf_counter()
            is_playing_a = True

        # also start playing b
        elif ((is_playing_a) and (not is_playing_b) and ((now - t0a) > (dtrack_a-5)) and (random.randint(0,100)<5)):
            # start playing b
            print("\t[_>>] B {} :: {} :: {} secs".format(time.ctime(), fns[i_b], dtrack_b))
            pygame.mixer.Sound.play(sndB)
            t0b = time.perf_counter()
            is_playing_b = True

    # make this on both manual and auto or even none mode
    # stop_playin_a
    if (is_playing_a and ((now - t0a) > dtrack_a) ):
        if (not is_playing_b):
            pygame.mixer.quit()
        is_playing_a = False
        print("\t[_==] A :: {} ".format(time.ctime(), current_dev))

    # stop_playin_b
    if (is_playing_b and ((now - t0b) > dtrack_b) ):
        if (not is_playing_a):
            pygame.mixer.quit()
        is_playing_b = False
        print("\t[_==] B :: {} ".format(time.ctime(), current_dev))
    return


# the loop from outside
def game_loop():
    while running:
        handle_events()
        handle_mouse_clicks()
        manage_sound()
        update_text()
        clock.tick(9)

# the main (init+loop)
def main():
    pygame.display.set_caption('[ ~~~~~ ]')
    if args['debug']:
        show_devices()
    init_osc(args['receiver_ip_a'], args['receiver_port_a'], args['receiver_ip_b'], args['receiver_port_b'])
    init_sound()
    pygame.time.set_timer(TIC_EVENT, TIC_TIMER)
    game_loop()
    print("[-_-] //...")

if __name__=="__main__":
    # argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--mode",               default="master",           help="send data to slaves") 
    ap.add_argument("-d", "--debug",              default="False",            help="enables verbose for debugging")
    ap.add_argument("-r", "--receiver-ip-a",      default="192.168.1.250",    help="receiver ip address slave a")
    ap.add_argument("-p", "--receiver-port-a",    default="57120",            help="receiver osc port slave a")
    ap.add_argument("-o", "--receiver-ip-b",      default="192.168.1.216",    help="receiver ip address slave b")
    ap.add_argument("-q", "--receiver-port-b",    default="57120",            help="receiver osc port slave b")
    args = vars(ap.parse_args())

    # real main
    main()










