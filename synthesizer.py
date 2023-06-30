from datetime import datetime
import multiprocessing
from recorder import record, RECORD_SECONDS
import pygame
from pygame.locals import *
import time
from equalizer import *

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(50)


piano_notes = {
    K_a: 'C',
    K_s: 'C#',
    K_d: 'D',
    K_f: 'D#',
    K_g: 'E',
    K_h: 'F',
    K_j: 'F#',
    K_x: 'G',
    K_c: 'G#',
    K_v: 'A',
    K_b: 'A#',
    K_n: 'B'
}

kalimba_notes = {
    K_a: 'A3',
    K_s: 'B',
    K_d: 'B3',
    K_f: 'C',
    K_g: 'C1',
    K_h: 'C2',
    K_j: 'D',
    K_q: 'D5',
    K_w: 'E5',
    K_e: 'F#',
    K_r: 'F2',
    K_t: 'F3',
    K_y: 'F4',
    K_u: 'G',
    K_i: 'G3',
}

classic_guitar_notes = {
    K_a: 'C',
    K_s: 'C#',
    K_d: 'D',
    K_f: 'D#',
    K_g: 'E',
    K_h: 'F',
    K_j: 'F#',
    K_k: 'G',
    K_l: 'G#',
    K_SEMICOLON: 'A',
    K_QUOTE: 'A#',
    K_BACKSLASH: 'B',
    K_q: 'C2',
    K_w: 'C#2',
    K_e: 'D2',
    K_r: 'D#2',
    K_t: 'E2',
    K_y: 'F2',
    K_u: 'F#2',
    K_i: 'G2',
    K_o: 'G#2',
    K_p: 'A2',
    K_LEFTBRACKET: 'A#2',
    K_RIGHTBRACKET: 'B2',
    K_z: 'E3'
}

instruments = {
    1: ('piano', piano_notes),
    2: ('classic_guitar', classic_guitar_notes),
    3: ('kalimba', kalimba_notes)
}

selected_instrument = int(input('Please select your instrument:\n1. Piano\n2. Classic Guitar\n3. Kalimba\nYour choice: '))

key_channels = {}

note_channels = {}

note_sounds = {}

if selected_instrument and instruments.get(selected_instrument):
    instrument = instruments[selected_instrument]
    instrument_notes = instrument[1]

    for i, key in enumerate(list(instrument_notes.keys())):
        key_channels[key] = i + 1

    for key, note in instrument_notes.items():
        sound_file = f'{instrument[0]}_notes/{note}.wav'  # Assuming you have WAV files for each note
        sound = pygame.mixer.Sound(sound_file)
        channel = pygame.mixer.Channel(key_channels[key])  # Assign channel based on the key value
        note_channels[key] = channel
        channel.set_endevent(USEREVENT + key)  # Set a unique end event for each channel
        note_sounds[key] = sound

    equalizer_startup(selected_instrument)
else:
    exit()


pressed_keys = {}

screen = pygame.display.set_mode((1, 1))
pygame.mixer.music.set_endevent(USEREVENT)

p1 = multiprocessing.Process(target=record)
p1.start()
start_time = datetime.now()
print('Recording is started.')
recording = True

while True:
    if recording:
        time_delta = datetime.now() - start_time
        if time_delta.total_seconds() >= RECORD_SECONDS:
            print('Recording is ended.')
            recording = False

    for event in pygame.event.get():
        if event.type == QUIT:
            equalizer_cleanup()
            pygame.quit()
            exit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                equalizer_cleanup()
                pygame.quit()
                exit()
            pressed_keys[event.key] = True

            if event.key in note_channels:
                channel = note_channels[event.key]
                if channel.get_busy():
                    channel.stop()
                channel.play(note_sounds[event.key])
                turn_on_equalizer_lights(instrument_notes[event.key])

        elif event.type == KEYUP:
            if event.key in pressed_keys:
                del pressed_keys[event.key]

        elif event.type >= USEREVENT:
            turn_off_equalizer_lights()
            still_active = []
            for key, channel in note_channels.items():
                if channel.get_busy():
                    still_active.append(instrument_notes[key])
            if still_active:
                turn_on_equalizer_lights(still_active)

    if len(pressed_keys) > 1:
        for key in pressed_keys:
            channel = note_channels[key]
            if channel.get_busy():
                channel.stop()
            channel.play(note_sounds[key])
            turn_on_equalizer_lights(instrument_notes[key])

    time.sleep(0.005)

