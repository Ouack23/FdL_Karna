<<<<<<< HEAD
import logging, sys, time, functions
=======
import logging, functions, sys
>>>>>>> 388ea43b06e4ceb96b24bec9e2a67bd4059e27c2
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    logging.error("Not a raspberry ! Quitting")
    sys.exit(0)
from collections import OrderedDict


class Pins(object):
<<<<<<< HEAD
    def __init__(self, pins):
        self.pins = pins
        self.gpio_setup("DEBUG")
        self.event = "wait"

    def get_keys(self):
        return self.pins.keys()

    def get_values(self):
        return self.pins.values()

=======
    def __init__(self):
        self.pins = OrderedDict()
        self.pins["b"] = 4
        self.pins["y"] = 17
        self.pins["g"] = 27
        self.pins["r"] = 22
        self.gpio_setup("DEBUG")
        self.event = "wait"

>>>>>>> 388ea43b06e4ceb96b24bec9e2a67bd4059e27c2
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

<<<<<<< HEAD
    def set_color_and_black(self, color, duration):
=======
    def set_color(self, color):
>>>>>>> 388ea43b06e4ceb96b24bec9e2a67bd4059e27c2
        self.cleanup_pins()
        GPIO.setup(self.pins.values(), GPIO.OUT, initial=GPIO.LOW)

        if color in self.pins:
            GPIO.output(self.pins[color], GPIO.HIGH)
<<<<<<< HEAD
            time.sleep(duration)
            GPIO.output(self.pins[color], GPIO.LOW)
=======
>>>>>>> 388ea43b06e4ceb96b24bec9e2a67bd4059e27c2

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
<<<<<<< HEAD
        self.gpio_set_inputs()

        if GPIO.wait_for_edge(self.pins.get(color), GPIO.RISING):
            logging.debug("Button " + str(color) + " pressed")
            self.event = self.pins.get(functions.search_key_with_value(color, self.pins))
            self.read_inputs()

    def get_first_wrong_color_event(self, color):
        self.event = "wait"
        self.gpio_set_inputs()

        for i in range(len(self.pins)):
            if self.pins.keys()[i] != color:
                GPIO.add_event_detect(self.pins.values()[i], GPIO.RISING, callback=self.first_color_name, bouncetime=500)

    def first_color_name(self, channel):
        self.event = functions.search_key_with_value(channel, self.pins)
=======

        if GPIO.wait_for_edge(self.pins.get(color), GPIO.RISING):
            logging.debug("Button " + str(color) + " pressed")
            self.read_inputs()

    def get_first_color_event(self, color):
        self.event = "wait"
        self.gpio_set_inputs()

        GPIO.add_event_detect(self.pins.get(color), GPIO.RISING, callback=self.first_color_name, bouncetime=1000)

        for i in range(len(self.pins)):
            if self.pins.keys()[i] != color:
                GPIO.add_event_detect(self.pins.values()[i], GPIO.RISING, callback=self.first_color_name, bouncetime=1000)

    def first_color_name(self, channel):
        self.event = channel
>>>>>>> 388ea43b06e4ceb96b24bec9e2a67bd4059e27c2

    def delete_event_detections(self):
        for i in range(len(self.pins)):
            GPIO.remove_event_detect(self.pins.values()[i])
<<<<<<< HEAD

    def is_pressed(self, color):
        self.gpio_set_inputs()

        return GPIO.input(self.pins.get(color)) == 1
=======
>>>>>>> 388ea43b06e4ceb96b24bec9e2a67bd4059e27c2
