import logging, functions
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    pass
from collections import OrderedDict


class Pins(object):
    def __init__(self):
        self.pins = OrderedDict()
        self.pins["b"] = 4
        self.pins["y"] = 17
        self.pins["g"] = 27
        self.pins["r"] = 22
        self.event = "wait"

    def gpio_setup(self, log_level):
        GPIO.setmode(GPIO.BCM)
        if log_level == "DEBUG":
            GPIO.setwarnings(True)
        else:
            GPIO.setwarnings(False)
        self.gpio_set_inputs()

    def cleanup_pins(self):
        GPIO.cleanup(self.pins.values())

    def get_colors(self):
        return self.pins.keys()

    def gpio_set_inputs(self):
        self.cleanup_pins()
        GPIO.setup(self.pins.values(), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def set_color(self, color):
        self.cleanup_pins()
        GPIO.setup(self.pins.values(), GPIO.OUT, initial=GPIO.LOW)

        if color in self.pins:
            GPIO.output(self.pins[color], GPIO.HIGH)

    def read_inputs(self):
        result = []
        self.gpio_set_inputs()
        logging.debug("Reading GPIO")

        for i in range(len(self.pins)):
            result.append(GPIO.input(self.pins.values()[i]))
            logging.debug("Result " + self.pins.keys()[i] + " = " + str(result[i]))

        return result

    def wait_for_color(self, color):
        self.gpio_set_inputs()
        self.event = "wait"

        if GPIO.wait_for_edge(self.pins.get(color), GPIO.RISING):
            logging.debug("Button " + str(color) + " pressed")
            self.read_inputs()

    def get_first_color_event(self, color):
        self.event = "wait"
        self.gpio_set_inputs()

        GPIO.add_event_detect(self.pins.get(color), GPIO.RISING, callback=self.good_first_color_name, bouncetime=200)

        for i in range(len(self.pins)):
            if self.pins.keys()[i] != color:
                GPIO.add_event_detect(self.pins.values()[i], GPIO.RISING, callback=self.wrong_first_color_name, bouncetime=200)

    def good_first_color_name(self, channel):
        self.event = "right"
        color = functions.search_key_with_value(channel, self.pins)

        if color is not None:
            logging.debug("GOOD : Detecting color " + str(color) + " as first event")
        else:
            logging.error("First event considered good but doesn't match a color !")

        self.delete_event_detections()

    def wrong_first_color_name(self, channel):
        self.event = "wrong"
        color = functions.search_key_with_value(channel, self.pins)

        if color is not None:
            logging.debug("WRONG : Detecting color " + str(color) + " as first event")
        else:
            logging.error("First event considered bad but doesn't match a color !")

        self.delete_event_detections()

    def delete_event_detections(self):
        self.event = "wait"
        for i in range(len(self.pins)):
            GPIO.remove_event_detect(self.pins.values()[i])
