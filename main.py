try:
    from RPi import GPIO
except RuntimeError:
    print("Error importing RPiGPIO! You need superuser privileges. Use 'sudo' to run your script")

GPIO.setmode(GPIO.BOARD)

GPIO.setup([4,10],GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup([12,18],GPIO.OUT)

