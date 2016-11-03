# -*- coding: utf-8 -*-
#
# GPIO tools
#

from settings import settings

if settings.get("sys", "raspi"):
    try:
        import pigpio
    except ImportError:
        settings["sys"]["raspi"] = False


rpi = None


def init_pigpio():
    global rpi
    rpi = pigpio.pi()
