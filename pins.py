import logging, warnings
import RPi.GPIO as GPIO
import DMX
from collections import OrderedDict

pins = OrderedDict(blue = 2, yellow = 3, green = 4, red = 14)


def gpio_setup():
    global pins

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(True)
    gpio_set_inputs()


def cleanup_pins():
    global pins

    GPIO.cleanup(pins.values())


def get_colors():
    global pins
    result = []

    for i in range(len(pins)):
        result.append(pins.keys()[i])

    logging.debug("Colors set to : " + DMX.array_to_string(result))

    return result

def gpio_set_inputs():
    global pins

    cleanup_pins()
    GPIO.setup(pins.values(), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def set_color(color):
    global pins

    cleanup_pins()
    GPIO.setup(pins.values(), GPIO.OUT, initial=GPIO.LOW)

    if color in pins:
        GPIO.output(pins[color], GPIO.HIGH)


def read_inputs():
    global pins

    result = []
    logging.debug("Reading GPIO")

    for i in range(len(pins)):
        result.append(GPIO.input(pins.values()[i]))
        logging.debug("Result " + pins.keys()[i] + " = " + str(result[i]))

    return result


def wait_for_color(color):
    global pins
    
    channel = pins.get(color)
    
    gpio_set_inputs()
    
    GPIO.add_event_detect(channel, GPIO.RISING)
    
    if GPIO.event_detected(channel):
        print('Button pressed')
