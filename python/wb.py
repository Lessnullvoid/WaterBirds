#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
[waterbirds // 22.01]

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
from oscpy.server import OSCThreadServer
from glob import glob
import time, random
import argparse
import serial, socket

args = None
mode = "master"
osc_client_a = None
osc_client_b = None
osc_server = None
osc_socket = None
serial_port=None

colors = [
    (24, 48, 48),   # Medium Jungle Green
    (216, 168, 96), # Streusel Cake
    (216, 96, 48),  # Tangerine Bliss
    (24, 96, 96),   # Emerald Pool
    (0, 48, 48),    # Daintree
    (212, 64, 38)   # more tanger
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
past_state = 0
# 0: select, 
# 1: auto,
# 2: manual menu, 
# 3: manual+sound, 
# 4: manual+pneum, 
# 5: manual both

# init
pygame.init()
window = pygame.display.set_mode((w, h))

# ------------------------------------------------------------------------
# choose base path
base_path = "/home/pi/WaterBirds/python"
#base_path = "/home/pi/waterbirds"
#base_path = "/media/emme/0A/SK/PY/waterbirds"
# ------------------------------------------------------------------------

font_path = base_path+'/RevMiniPixel.ttf'
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
sounds_path = base_path+'/ogg'
sndA = None
sndB = None
fns = []
current_dev = None
t0a = 0
t0b = 0
i_a = 0
i_b = 0

# ------------------------------------------------------------------------
# names of the devices
device_a = "Built-in Audio Analog Stereo"
#device_b = "Audio Adapter (Planet UP-100, Genius G-Talk) Analog Stereo"
device_b = "Sound BlasterX G1 Analog Stereo"
# serial port name
serial_name = "/dev/ttyUSB0"
# ---------------------------------------------------------------------------


def show_devices():
    # show the audio playback devices
    is_capture = 0 
    num = sdl2.get_num_audio_devices(is_capture)
    devices = [str(sdl2.get_audio_device_name(i, is_capture), encoding="utf-8") for i in range(num)]
    print("\n".join(devices))
    return

# -osc
def got_message(*values):
    print("\n\n[:OSC:] got values: {}\n".format(values))

# --------------------------------------------------------------------------------------------------------------
def init_comms(ha_ = "192.168.1.136", pa_ = 9105, hb_ = "192.168.1.250", pb_ = 9106, hs_="0.0.0.0", ps_=9300 ):
    # host a, port a, host b, port b, host server, port server
    global osc_client_a, osc_client_b, osc_server, osc_socket, serial_port
    # init the osc comms
    osc_client_a = OSCClient(ha_, pa_)
    osc_client_b = OSCClient(hb_, pb_)
    osc_server = OSCThreadServer()
    osc_socket = osc_server.listen(address=hs_, port=ps_, default=True)
    osc_server.bind(b'/waterbirds/slave', got_message, osc_socket)
    osc_server.listen()
    print ("[osc] client A at: {}".format(osc_client_a))
    print ("[osc] client B at: {}".format(osc_client_b))
    print ("[osc] server S at: {}".format(osc_server))
    # init the serial comms
    serial_port = serial.Serial(serial_name, 115200, timeout=0.050)
    serial_port.write("ready\n".encode())
    """ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate = 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
        )"""
    return


def update_comms():
    global osc_client_a, osc_client_b, past_state, state, in_auto, in_manual
    # add past_state and send messages when transition from select to auto    
    if state==1 and past_state==0:
        # from select to auto
        ruta = '/waterbirds/auto'
        ruta = ruta.encode()
        osc_client_a.send_message(ruta, [1])
        osc_client_b.send_message(ruta, [1])
        serial_port.write("ready\n".encode())
        past_state = state
    if state==3 and past_state==2:
        # from manual sel to sound
        ruta = '/waterbirds/sound'
        ruta = ruta.encode()
        osc_client_a.send_message(ruta, [1])
        osc_client_b.send_message(ruta, [1])
        past_state = state
    if state==4 and past_state==2:
        # from manual sel to pneum
        ruta = '/waterbirds/pneum'
        ruta = ruta.encode()
        osc_client_a.send_message(ruta, [1])
        osc_client_b.send_message(ruta, [1])
        serial_port.write("ready\n".encode())
        past_state = state
    if state==5 and past_state==2:
        # from manual sel to both
        ruta = '/waterbirds/manual'
        ruta = ruta.encode()
        osc_client_a.send_message(ruta, [1])
        osc_client_b.send_message(ruta, [1])
        serial_port.write("ready\n".encode())
        past_state = state
    if state==0 and past_state>0 and past_state<6:
        # from any to sel, it is, stop
        ruta = '/waterbirds/stop'
        ruta = ruta.encode()
        osc_client_a.send_message(ruta, [1])
        osc_client_b.send_message(ruta, [1])
        if (past_state!=3):
            serial_port.write("stop\n".encode())
        past_state = state
    return

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

def exit():
    osc_server.close()
    #serial_port.release()
    print("[+-+] quitting waterbirds")
    return

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
    global state, past_state, in_auto, in_manual
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
                    past_state = state
                    state = 1
                    print("\n\n[B{}]: ~AUTO~ mode -------------".format(j))
                    time.sleep(0.2)
                elif (j==1 and not (in_auto or in_manual)):
                    in_manual = True
                    past_state = state
                    state = 2
                    print("\n\n[B{}]: ~MANUAL~ mode -----------".format(j))
                    time.sleep(0.2)
    elif state==1:
        for j,b in enumerate(btns_running):
            if (b.collidepoint(pos) and pressed1):
                if(j==1 and in_auto):
                    in_auto = False
                    past_state = state
                    state = 0
                    print("[B{}]: -------------- ~AUTO~ stopped\n\n".format(j))
                    time.sleep(0.2)
    elif state==2: 
        for j,b in enumerate(btns_manual):
            if (b.collidepoint(pos) and pressed1):
                if(j==0 and in_manual):
                    past_state = state
                    state = 3
                    print("[B{}]: ~MANUAL SOUND ONLY ".format(j))
                    time.sleep(0.2)
                elif(j==1 and in_manual):
                    past_state = state
                    state = 4
                    print("[B{}]: ~MANUAL PNEUM ONLY ".format(j))
                    time.sleep(0.2)
                elif(j==2 and in_manual):
                    past_state = state
                    state = 5
                    print("[B{}]: ~MANUAL BOTH ".format(j))
                    time.sleep(0.2)
    elif state==3 or state==4 or state==5:
        for j,b in enumerate(btns_running):
            if (b.collidepoint(pos) and pressed1):
                if(j==1 and in_manual):
                    in_manual = False
                    past_state = state
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
            window.blit(lab, (int(w/2 - 55), 170+j*240))
    pygame.display.flip()



def init_sound():
    global fns, t0a, t0b, delay_btwn, dtrack_a, dtrack_b, rdelay
    fns = glob(sounds_path+"/*.ogg")
    fns.sort()
    print ("\n".join(fns))
    # play_timers reference
    t0a = 0
    t0b = 0
    delay_btwn = 30
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
    if in_auto or (in_manual and (state==3 or state==5)):
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
        update_comms()
        clock.tick(9)

# the main (init+loop)
def main():
    pygame.display.set_caption('[ ~~~~~ ]')
    if args['debug']:
        show_devices()
    init_comms()
    #init_comms(args['receiver_ip_a'], int(args['receiver_port_a']), args['receiver_ip_b'], int(args['receiver_port_b']))
    init_sound()
    pygame.time.set_timer(TIC_EVENT, TIC_TIMER)
    game_loop()
    print("[-_-] //...")
    exit()
    return

if __name__=="__main__":
    # argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--mode",               default="master",           help="send data to slaves") 
    ap.add_argument("-d", "--debug",              default="False",            help="enables verbose for debugging")
    ap.add_argument("-r", "--receiver-ip-a",      default="192.168.1.250",    help="receiver ip address slave a")
    ap.add_argument("-p", "--receiver-port-a",    default="57120",            help="receiver osc port slave a")
    ap.add_argument("-s", "--receiver-ip-b",      default="192.168.1.216",    help="receiver ip address slave b")
    ap.add_argument("-q", "--receiver-port-b",    default="57120",            help="receiver osc port slave b")
    args = vars(ap.parse_args())

    # real main
    main()










