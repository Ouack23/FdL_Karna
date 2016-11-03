# -*- coding: utf-8 -*-
#
# Master module to run them all
#
#

import termios, sys, os
import threading
TERMIOS = termios

import lib.settings

lib.settings.init()

from lib.settings import settings
if settings.get("sys", "raspi"):
    try:
        import pigpio
    except ImportError:
        settings["sys"]["raspi"] = False
import logger
import vthread
# import lib.system
# import lib.clock
# import lib.dmx
import ui
#import lib.sound
import sensor
import gpio
import card
import clock
import lightfile
import dmx
import modulation



from logger import init_log
log = init_log("master")


senscard = None
clockthread = None
shutdown = None


def main_init():
    global senscard, clockthread, shutdown
    shutdown = threading.Event()
    senscard = card.CardDriver()
    clockthread = clock.ClockThread()
    senscard.start_sensor(clockthread)
    #lfile = lightfile.LightFile(settings.get("lightfile", "name"))
    lfile = lightfile.LightFile("kfet.csv.lf")
    lfile.read()
    dmxthread = dmx.DmxThread(lfile)
    modthread = modulation.DmxModulationThread(lfile, senscard.sensor_thread)
    clockthread.set_thread_dmx(dmxthread)
    clockthread.set_thread_dmxmod(modthread)
    dmxthread.start()
    modthread.start()


def main_start_clock():
    global clockthread
    clockthread.start()


def main_exit():
    global senscard, shutdown
    vthread.quit_all_threads()
    senscard.shutdown()
    shutdown.set()


def should_shutdown():
    global shutdown
    return shutdown.is_set()





def getkey():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
    new[6][TERMIOS.VMIN] = 1
    new[6][TERMIOS.VTIME] = 0
    termios.tcsetattr(fd, TERMIOS.TCSANOW, new)
    c = None
    try:
        c = os.read(fd, 1)
    finally:
        termios.tcsetattr(fd, TERMIOS.TCSAFLUSH, old)
    return c

def getch():
    """Waits for a single keypress on stdin.

    This is a silly function to call if you need to do it a lot because it has
    to store stdin's current setup, setup stdin for reading single keystrokes
    then read the single keystroke then revert stdin back after reading the
    keystroke.

    Returns the character of the key that was pressed (zero on
    KeyboardInterrupt which can happen when a signal gets handled)

    """
    import termios, fcntl, sys, os
    fd = sys.stdin.fileno()
    # save old state
    flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
    attrs_save = termios.tcgetattr(fd)
    # make raw - the way to do this comes from the termios(3) man page.
    attrs = list(attrs_save) # copy the stored version to update
    # iflag
    attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                  | termios.ISTRIP | termios.INLCR | termios. IGNCR
                  | termios.ICRNL | termios.IXON )
    # oflag
    attrs[1] &= ~termios.OPOST
    # cflag
    attrs[2] &= ~(termios.CSIZE | termios. PARENB)
    attrs[2] |= termios.CS8
    # lflag
    attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                  | termios.ISIG | termios.IEXTEN)
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    # turn off non-blocking
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
    # read a single keystroke
    try:
        ret = sys.stdin.read(1) # returns a single character
    except KeyboardInterrupt:
        ret = 0
    finally:
        # restore old state
        termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
    return ret


def emulate_input():
    global senscard
    while True:
        char = getkey()
        if char in ("q", "Q", "e"):
            return
        elif char == "w":
            log.debug("w: left")
            senscard.display.recv_push_left()
        elif char == "x":
            log.debug("x: ok")
            senscard.display.recv_push_ok()
        elif char == "c":
            log.debug("c: right")
            senscard.display.recv_push_right()
        else:
            print(char)

# def getch():   # define non-Windows version
#     import sys, tty, termios
#     fd = sys.stdin.fileno()
#     old_settings = termios.tcgetattr(fd)
#     try:
#         tty.setraw(sys.stdin.fileno())
#         ch = sys.stdin.read(1)
#     finally:
#         termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#     return ch