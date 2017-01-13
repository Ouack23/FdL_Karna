import logging, warnings
import RPi.GPIO as GPIO
from DMX import array_to_string
from collections import OrderedDict


pins = OrderedDict({'blue':  4, 'yellow': 17, 'green': 27, 'red': 22})


def gpio_setup(log_level):
    global pins, logger
    GPIO.setmode(GPIO.BCM)
    if log_level == "DEBUG":
    	GPIO.setwarnings(True)
    else:
        GPIO.setwarnings(False)
    gpio_set_inputs()


def cleanup_pins():
    global pins
    GPIO.cleanup(pins.values())


def get_colors():
    global pins
    return pins.keys()


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
    gpio_set_inputs()
    logging.debug("Reading GPIO")
    
    for i in range(len(pins)):
        result.append(GPIO.input(pins.values()[i]))
        logging.debug("Result " + pins.keys()[i] + " = " + str(result[i]))

    return result


def wait_for_color(color):
    global pins
    
    channel = pins.get(color)
    gpio_set_inputs()
    if GPIO.wait_for_edge(channel, GPIO.RISING):
        print('Button pressed')
        read_inputs()
