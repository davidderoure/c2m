'''

Experimental code to test xbox controller generating midi

Tested in python 3.10.8 and pygame 2.1.2

DDeR 2022-10-16
Updated 2022-10-27

The test mapping is that Button A generates midi note on and off events
when pressed and released, and the pitch and velocity of those events is
determined by the right hand joystick (pitch increasing left to right,
velocity increasing bottom to top).  Meanwhile the left rear control sends
pitch bend messages (up only).

Left joystick, left to riught is axis 0 -1 to 1
Left joystik, top to bottom is axis 1, -1 to 1
Press left joystick is button 8
Right joystick, left to riught is axis 2 -1 to 1
Right joystik, top to bottom is axis 3, -1 to 1
Left back, axis 4 default position -1 goes to 1
Right back, axis 5 default position -1 goes to 1
Press right joystick is button 9
Button A is button 0
Button B is button 1
Button X is button 2
Button Y is button 3
Hat L=(-1,0). R=(1,0) up=(0,1) down=(0,-1)


'''

import pygame
import pygame.midi
from time import sleep

# Some handy GM instruments

GRAND_PIANO = 0
HARPSICHORD = 7
CHURCH_ORGAN = 19
ACOUSTIC_BASS = 33
VIOLIN = 41
TENOR_SAX = 67
FLUTE = 74

instrument = FLUTE

# Report available MIDI devices

def midiListDevices():
    output_count = 0

    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"
            output_count = output_count + 1

        print ("%2i: interface :%s:, name :%s:, opened :%s:  %s" %
               (i, interf, name, opened, in_out))

    print(output_count, " MIDI outputs available")
    return output_count

# Generate a few MIDI notes to help with testing

def midiFanfare():

    global midi_out

    midi_out.note_on(62,127) # D
    sleep(0.5)

    midi_out.note_on(67,127) # G
    sleep(0.5)

    midi_out.note_on(72,127) # C
    sleep(0.5)

    midi_out.note_on(77,127) # F
    sleep(1.0)
   
    midi_out.note_off(62)
    midi_out.note_off(67)
    midi_out.note_off(72)
    midi_out.note_off(77)

# Report details from game controller(s)

def listControls():
    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()
    print("Number of controllers: ", joystick_count)
     
    # Report each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
     
        name = joystick.get_name()
        print("Joystick name: ", name)
     
        axes = joystick.get_numaxes()
        print("Number of axes: ", axes)
     
        buttons = joystick.get_numbuttons()
        print("Number of buttons: ", buttons)
     
        hats = joystick.get_numhats()
        print("Number of hats: ", hats)
    
# Simple main event loop

def eventLoop():
    global joystick
    global midi_out

    done = False
    sounding = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
     
            # Possible joystick actions: 
            # JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN
            # JOYBUTTONUP JOYHATMOTION
    
            if event.type == pygame.JOYBUTTONDOWN:
                button = joystick.get_button(0)
                if button == 1 and not sounding:
                    pitch = int(joystick.get_axis(0) * 24 + 60)
                    velocity = int(joystick.get_axis(1) * -63 + 63)
                    midi_out.note_on(pitch, velocity)
                    sounding = True
                    
            if event.type == pygame.JOYBUTTONUP:
                button = joystick.get_button(0)
                if button == 0 and sounding:
                    midi_out.note_off(pitch)
                    sounding = False

# This extended event loop calls out to functions in response to events

def eventLoop2():
    global joystick
    global midi_out
    global sounding

    # local

    buttons = joystick.get_numbuttons()
    axes = joystick.get_numaxes()
    hats = joystick.get_numhats()

    # initialise state arrays

    button_state = [0 for x in range(buttons)]
    axes_state = [0 for x in range(axes)]

    for i in range(buttons):
        button_state[i] = joystick.get_button(i)

    for i in range(axes):
        axes_state[i] = joystick.get_axis(i)

    done = False
    sounding = False

    # LOOP

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
     
            # Possible joystick actions: 
            # JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN
            # JOYBUTTONUP JOYHATMOTION
    
            if event.type == pygame.JOYBUTTONDOWN:
                for i in range(buttons):
                    if button_state[i] != joystick.get_button(i):
                        button_down(i)
                        button_state[i] = joystick.get_button(i)

            if event.type == pygame.JOYBUTTONUP:
                for i in range(buttons):
                    if button_state[i] != joystick.get_button(i):
                        button_up(i)
                        button_state[i] = joystick.get_button(i)

            if event.type == pygame.JOYAXISMOTION:
                for i in range(axes):
                    if axes_state[i] != joystick.get_axis(i):
                        axis_motion(i, joystick.get_axis(i))
                        axes_state[i] = joystick.get_axis(i)

def button_down(i):
    global sounding, pitch

    if i == 0 and not sounding:
        pitch = int(joystick.get_axis(0) * 24 + 60)
        velocity = int(joystick.get_axis(1) * -63 + 63)
        midi_out.note_on(pitch, velocity)
        sounding = True
    else:
        print("button", i, "down")

def button_up(i):
    global sounding, pitch

    if i == 0 and sounding:
        midi_out.note_off(pitch)
        sounding = False
    else:
        print("button", i, "up")

def axis_motion(i, x):
    global sounding

    # The value is a signed integer from -8192 to +8191. For example, 
    # 0 means "no change", +4096 is typically a semitone higher, 
    # and -8192 is 1 whole tone lower 

    if i == 4 and sounding:
        midi_out.pitch_bend(int(x * 4095 + 4096))
    # else:
        # print("axis", i, x)

# MAIN

# Init MIDI

pygame.init()
pygame.midi.init()
 
if midiListDevices() == 0:
    print("No MIDI outout devices found")
    exit()

port = int(input("Enter output device number: "))
midi_out = pygame.midi.Output(port, 0)  # GLOBAL
print("Using: ", port)
midi_out.set_instrument(instrument)
midiFanfare()

# Init joystick

pygame.joystick.init()

listControls()

if pygame.joystick.get_count() == 0:
    print("No controller found")
    exit()

joystick = pygame.joystick.Joystick(0)  # GLOBAL Using joystick index 0

sounding = False # Global used for eventLoop2()

eventLoop2()

# End of c2m.py
