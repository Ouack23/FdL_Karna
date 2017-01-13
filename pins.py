import logging
import RPi.GPIO as GPIO


def gpio_setup():
    inputs = [2]
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(True)
    GPIO.setup(inputs, GPIO.INPUT)
