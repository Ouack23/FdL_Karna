import logging
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error !")


def gpio_setup():
    inputs = [2]
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(True)
    GPIO.setup(inputs, GPIO.OUT)
