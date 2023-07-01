import os

def record():
    monitor = 'alsa_output.platform-bcm2835_audio.analog-stereo.monitor'
    os.system(f'parec -d {monitor} | lame -r -V0 - OutputAudio.mp3 & sleep 20; kill $!')
    print('Recording is ended.')

