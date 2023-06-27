import RPi.GPIO as GPIO

piano_notes_freq = {
    'C': 130.8,
    'C#': 138.6,
    'D': 146.9,
    'D#': 155.6,
    'E': 164.8,
    'F': 174.6,
    'F#': 185,
    'G': 196,
    'G#': 207.6,
    'A': 220,
    'A#': 233.1,
    'B': 247
}

classic_guitar_freq = {
    'C': 32.7,
    'C#': 34.6,
    'D': 36.7,
    'D#': 38.9,
    'E': 41.2,
    'F': 43.6,
    'F#': 46.2,
    'G': 49,
    'G#': 51.9,
    'A': 55,
    'A#': 58.3,
    'B': 61.7,
    'C2': 65.4,
    'C#2': 69.2,
    'D2': 73.4,
    'D#2': 77.8,
    'E2': 82.4,
    'F2': 87.3,
    'F#2': 92.5,
    'G2': 98,
    'G#2': 103.8,
    'A2': 110,
    'A#2': 116.5,
    'B2': 123.5,
    'E3': 164.8
}

instruments = {
    1: ('piano', piano_notes_freq, 120, 240),
    2: ('classic_guitar', classic_guitar_freq, 30, 150)
}

PWM_FREQUENCY = 100
DUTY_CYCLE = 50
LED_PINS = [i for i in range(1, 15)]
LED_FREQ = {}
GPIO_PWM = {}
PWM_DUTY_CYCLE = {}
GPIO_STAT = {}
note_frequencies = {}


def equalizer_startup(instrument):
    global note_frequencies
    note_frequencies = instruments[instrument][1]
    min_f, max_f = instruments[instrument][2], instruments[instrument][3]
    step = (max_f - min_f) / 12
    GPIO.setmode(GPIO.BCM)
    for i, pin in enumerate(LED_PINS):
        GPIO.setup(pin, GPIO.OUT)
        GPIO_PWM[pin] = GPIO.PWM(pin, PWM_FREQUENCY)
        PWM_DUTY_CYCLE[pin] = 0
        GPIO_STAT[pin] = False
        LED_FREQ[pin] = min_f + (step * i)


def turn_on_equalizer_lights(note):
    if isinstance(note, list):
        note_freq = max(list(map(lambda x: note_frequencies[x], note)))
    else:
        note_freq = note_frequencies[note]
    last_feq = 0
    for pin, freq in LED_FREQ.items():
        is_pwm_active = bool(not(PWM_DUTY_CYCLE[pin] == 0))

        if freq < note_freq:
            if is_pwm_active:
                GPIO_PWM[pin].ChangeDutyCycle(100)
                PWM_DUTY_CYCLE[pin] = 100
            GPIO.output(pin, GPIO.HIGH)
            GPIO_STAT[pin] = True
            last_feq = freq
        else:
            intensity = int(((note_freq - last_feq) / (freq - last_feq)) * 100)
            if not is_pwm_active and GPIO_STAT[pin]:
                break
            if is_pwm_active and PWM_DUTY_CYCLE[pin] > intensity:
                break
            GPIO_PWM[pin].start(DUTY_CYCLE)
            GPIO_PWM[pin].ChangeDutyCycle(intensity)
            PWM_DUTY_CYCLE[pin] = intensity
            GPIO_STAT[pin] = True
            break


def turn_off_equalizer_lights():
    for pin in LED_PINS:
        GPIO_PWM[pin].stop()
        PWM_DUTY_CYCLE[pin] = 0
        GPIO.output(pin, GPIO.LOW)
        GPIO_STAT[pin] = False


def equalizer_cleanup():
    turn_off_equalizer_lights()
    GPIO.cleanup()
