import logging, warnings
import RPi.GPIO as GPIO
from DMX import array_to_string
from collections import OrderedDict


pins = OrderedDict()
pins["blue"] = 4
pins["yellow"] =  17
pins["green"] =  27
pins["red"] = 22


def search_key_with_value(v, tab):
    for k, j in tab.items():
        if j == v:
            return k

    return None


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
    
    gpio_set_inputs()
    
    if GPIO.wait_for_edge(pins.get(color), GPIO.RISING):
        logging.debug("Button " + str(color) + " pressed")
        read_inputs()


def get_first_color_event(color):
    global pins
    
    gpio_set_inputs()
        
    GPIO.add_event_detect(pins.get(color), GPIO.RISING, callback=good_first_color_name, bouncetime=200)

    for i in range(len(pins)):
        if pins.keys()[i] != color:
            GPIO.add_event_detect(pins.values()[i], GPIO.RISING, callback=wrong_first_color_name, bouncetime=200)
    

def good_first_color_name(channel):
    global pins
    
    color = search_key_with_value(channel, pins)

    if color != None:
        logging.debug("GOOD : Detecting color " + str(color) + " as first event")
    else:
        logging.error("First event considered good but doesn't match a color !")

    delete_event_detections()


def wrong_first_color_name(channel):
    global pins
    
    color = search_key_with_value(channel, pins)
    
    if color != None:
        logging.debug("WRONG : Detecting color " + str(color) + " as first event")
    else:
        logging.error("First event considered bad but doesn't match a color !")

    delete_event_detections()


def delete_event_detections():
    global pins
    
    for i in range(len(pins)):
        GPIO.remove_event_detect(pins.values()[i])
