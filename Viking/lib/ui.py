# -*- coding: utf-8 -*-
#
# This file provide classes and tools to display the UI
#

import time
import threading

#import RPi.GPIO as GPIO

import gpio

from settings import settings
if settings.get("sys", "raspi"):
    import pigpio
from logger import init_log

log = init_log("ui")




class LedDriver(object):
    """
    LED Driver
    """

    def __init__(self, outpin, on=True):
        """
        :param outpin:
        :return:
        """
        self.on = on
        self.outpin = outpin
        if settings.get("sys", "raspi"):
            gpio.rpi.set_mode(outpin, pigpio.OUTPUT)
        #GPIO.setup(outpin, GPIO.OUT)
        self._value = None

    def set_on(self):
        """
        Set the led ON
        :return:
        """
        #GPIO.output(self.outpin, self.on)
        if settings.get("sys", "raspi"):
            gpio.rpi.write(self.outpin, self.on)

    def set_off(self):
        """
        Set the led OFF
        :return:
        """
        # GPIO.output(self.outpin, not self.on)
        if settings.get("sys", "raspi"):
            gpio.rpi.write(self.outpin, not self.on)

    def keep_on(self):
        """
        Set and keep on if relased
        :return:
        """
        self._value = True
        self.set_on()

    def keep_off(self):
        """
        Set and keep off if relased
        :return:
        """
        self._value = False
        self.set_off()

    def released(self):
        """
        Reset the led to the _value
        :return:
        """
        if self._value is None:
            log.warning("Released an unset led")
            return
        elif self._value is True:
            self.set_on()
        elif self._value is False:
            self.set_off()

    def blink(self, delay=200):
        """
        Just blink the led
        :param delay: ms delay
        :return:
        """
        delay /= 1000   # ms conversion
        self.set_off()
        time.sleep(delay/4.0)
        self.set_on()
        time.sleep(delay/2.0)
        self.set_off()
        time.sleep(delay/4.0)
        self.released()

def get_name_call(name):
        """
        :return:
        """
        def fnct(*args):
            log.debug("{0} pushed".format(name))
        return fnct


class InputDriver(object):
    """
    This class provide an input driver with deboucing
    """
    def __init__(self, name, fnct_rise=None, fnct_fall=None, bouncetime=None):
        """
        :return:
        """
        if bouncetime is None:
            self.bouncetime = settings.get("i/o", "bouncetime")
        else:
            self.bouncetime = bouncetime
        self.inpin = int(settings.get("i/o", "button", name))
        log.debug("name : {0}, pin : {1}".format(name, self.inpin))
        if settings.get("sys", "raspi"):
            gpio.rpi.set_mode(self.inpin, pigpio.INPUT)
            gpio.rpi.set_pull_up_down(self.inpin, pigpio.PUD_UP)
            gpio.rpi.set_noise_filter(self.inpin, self.bouncetime, self.bouncetime*2)
        self.name = name
        self.fnct_rise = fnct_rise
        self.fnct_fall = fnct_fall
        self.attach_fnct()
        self.set_fnct_rise(get_name_call(self.name))

    def attach_fnct(self):
        """
        Attach function to event by reseting them and reattach wia GPIO lib
        :return:
        """
        #GPIO.remove_event_detect(self.inpin)
        if self.fnct_rise is not None:
            #GPIO.add_event_detect(self.inpin, GPIO.RISING, callback=self.fnct_rise, bouncetime=self.bouncetime)
            if settings.get("sys", "raspi"):
                gpio.rpi.callback(self.inpin, pigpio.RISING_EDGE, self.fnct_rise)
        if self.fnct_fall is not None:
            if settings.get("sys", "raspi"):
                gpio.rpi.callback(self.inpin, pigpio.FALLING_EDGE, self.fnct_fall)
            #GPIO.add_event_detect(self.inpin, GPIO.FALLING, callback=self.fnct_fall, bouncetime=self.bouncetime)

    def set_fnct_rise(self, fnct):
        self.fnct_rise = fnct
        self.attach_fnct()

    def set_fnct_fall(self, fnct):
        self.fnct_fall = fnct
        self.attach_fnct()


class Display(object):
    """
    This class represent the display
    """

    def __init__(self, disp=None, led_status=None):
        """
        :param disp: optionnal disp object
        :param led_status: optionnal led state driver to validate
        :return:
        """
        self.display = disp
        self.led_status = led_status
        self.current_show = None  # Show to display
        self.parent_show = list()  # Previous show in order to keep a hierarchy
        self.txt_buffer = "    "  # Text buffer to show
        self._last_ok = 0
        self._last_left = 0
        self._last_right = 0
        self.bouncetime = settings.get("i/o", "bouncetime") / 1000.0

    def update_display(self, disp_float=False, decimals=0):
        """
        This method update the display with the txt_buffer
        :param disp_float: True to force float display
        :param decimals: number of decimals to show
        :return:
        """
        if self.display is not None:
            self.display.clear()
            if disp_float:
                self.display.print_float(self.txt_buffer, decimals)
            else:
                self.display.print_number_str(self.txt_buffer)
            self.display.write_display()
        else:
            print(self.txt_buffer)

    def recv_push_ok(self, *args):
        """
        This method transmit the push ok signal to the current show
        :return:
        """
        if time.time() - self._last_ok <= self.bouncetime:
            log.debug("debounce ok")
            return
        self._last_ok = time.time()
        if self.led_status is not None:
            self.led_status.blink()
        log.debug("display : pushed ok")
        if self.current_show is not None:
            self.current_show.push_ok()
        else:
            log.debug("Push ok ignore because there is no current show")

    def recv_push_right(self, *args):
        """
        This method transmit the push right signal to the current show
        :return:
        """
        if time.time() - self._last_right <= self.bouncetime:
            log.debug("debounce right")
            return
        self._last_right = time.time()
        if self.led_status is not None:
            self.led_status.blink()
        log.debug("display : pushed right")
        if self.current_show is not None:
            self.current_show.push_right()
        else:
            log.debug("Push right ignore because there is no current show")

    def recv_push_left(self, *args):
        """
        This method transmit the push left signal to the current show
        :return:
        """
        if time.time() - self._last_left <= self.bouncetime:
            log.debug("debounce left")
            return
        self._last_left = time.time()
        if self.led_status is not None:
            self.led_status.blink()
        log.debug("display : pushed left")
        if self.current_show is not None:
            self.current_show.push_left()
        else:
            log.debug("Push left ignore because there is no current show")


class Show(object):
    """
    Basic show object to be displayed
    """

    def __init__(self, display):
        """
        :param display: Display object
        :return:
        """
        self.display = display

    def enter(self):
        """
        This method is called when the show is called
        :return:
        """
        log.debug("enter..")
        self.start_display()
        self.display.current_show = self

    def quit(self):
        """
        This method is called when the show stop to be the current one
        :return:
        """
        self.stop_display()
        self.display.current_show = None

    def start_display(self):
        """
        This method is called when the Display start to show this
        :return:
        """
        pass

    def stop_display(self):
        """
        This method is called when the Display stop to show this
        :return:
        """
        pass


class ShowMenu(Show):
    """
    Basic show menu to be displayed
    """

    def __init__(self, display):
        """
        :param display: Display object
        :return:
        """
        Show.__init__(self, display)

    def enter(self):
        """
        This method is called when the menu is started
        :return:
        """
        #self.display.parent_show.append(self)
        Show.enter(self)

    def quit(self):
        """
        This method is called when the menu is stopped
        :return:
        """
        if self != self.display.parent_show.pop():
            log.error("SHOULD BE THE SAME")
        Show.quit(self)

    def push_ok(self):
        """
        This method is called when the button OK is pressed
        :return:
        """
        log.debug("PUSHED OK .. nothing to do")

    def push_right(self):
        """
        This method is called when the button RIGHT (>) is pressed
        :return:
        """
        log.debug("PUSHED > .. nothing to do")

    def push_left(self):
        """
        This method is called when the button LEFT (<) is pressed
        :return:
        """
        log.debug("PUSHED < .. nothing to do")


class ShowMenuStatic(ShowMenu):
    """
    This class represent a Menu with a static name
    """

    def __init__(self, display, txt):
        """
        :param display: Display object
        :param txt: txt to display
        :return:
        """
        ShowMenu.__init__(self, display)
        self.txt = txt  # txt[0:min(4, len(txt))]

    def start_display(self):
        log.debug("Menu static : => {0}".format(self.txt))
        self.display.txt_buffer = self.txt
        self.display.update_display()

    def stop_display(self):
        log.debug("Menu static : <= {0}".format(self.txt))
        self.display.txt_buffer = "    "
        self.display.update_display()

    def __repr__(self):
        return self.txt


class ShowMenuLive(ShowMenu):
    """
    This class represent a Menu with a static name
    """

    def __init__(self, display, fnct, args, framerate=None):
        """
        :param display: Display object
        :param fnct: function to call eahc time
        :param args: args to gave to the function
        :param framerate: display framerate
        :return:
        """
        ShowMenu.__init__(self, display)
        self._live_fnct = fnct
        self._live_fnct_args = args
        self._stop_thread = threading.Event()
        self._live_thread = None
        if framerate is None:
            framerate = settings.get("i/o", "display", "framerate")
        self._live_dt = 1.0/framerate

    def start_display(self):
        log.debug("start live disp")
        self._stop_thread.clear()
        self._live_thread = threading.Thread(target=self._live_fnct, args=[self, ]+self._live_fnct_args)
        self._live_thread.start()

    def stop_display(self):
        self._stop_thread.set()
        self._live_thread.join()


class ShowMenuTree(ShowMenuStatic):
    """
    This class represent a menu with an arboresance
    """

    def __init__(self, disp, txt):
        """
        :param disp: Display object
        :param txt:
        :return:
        """
        ShowMenuStatic.__init__(self, disp, txt)
        self.cursor = 0
        self.elements = list()

    def push_right(self):
        """
        Show next menu
        :return:
        """
        if len(self.elements) == 0:
            log.warning("Useless right shift on a empty menutree")
            return
        self.cursor += 1
        self.elements[(self.cursor - 1) % len(self.elements)].stop_display()
        self.elements[self.cursor % len(self.elements)].start_display()

    def push_left(self):
        """
        Show previous menu
        :return:
        """
        if len(self.elements) == 0:
            log.warning("Useless left shift on a empty menutree")
            return
        self.cursor -= 1
        self.elements[(self.cursor + 1) % len(self.elements)].stop_display()
        self.elements[self.cursor % len(self.elements)].start_display()

    def push_ok(self):
        """
        Enter submenu
        :return:
        """
        if len(self.elements) == 0:
            log.warning("There is no menu to select")
            return
        if isinstance(self.elements[self.cursor % len(self.elements)], ShowMenuTree):
            self.elements[self.cursor % len(self.elements)].enter()
        else:
            self.elements[self.cursor % len(self.elements)].push_ok()
            log.debug("Not entered because it's not a ShowMenuTree subclass")

    def enter(self):
        """
        Entering menu
        :return:
        """
        ShowMenuStatic.enter(self)
        if self.display.current_show is not None:
            self.display.parent_show.append(self.display.current_show)
        self.display.current_show = self
        log.debug("Enter tree : {1} \n{0}".format(self.display.parent_show, self.txt))
        if len(self.elements) > 0:
            self.elements[0].start_display()

    def quit(self):
        """
        Quitting menu
        :return:
        """
        ShowMenuStatic.quit(self)
        if len(self.display.parent_show) > 0:
            self.display.parent_show.pop().enter()
            log.debug("Return to {0}".format(self.display.current_show.txt))

    def back_quit(self):
        """
        Back quit
        :param self:
        :return:
        """
        self.display.current_show.quit()


class ShowMenuTreeLive(ShowMenuTree, ShowMenuLive):

    def __init__(self, display, fnct, args, framerate=None):
        """

        :param display:
        :param fnct:
        :param args:
        :param framerate:
        :return:
        """
        ShowMenuLive.__init__(self, display, fnct, args, framerate)
        ShowMenuTree.__init__(self, display, "")

    def start_display(self, *args, **kwargs):
        return ShowMenuLive.start_display(self, *args, **kwargs)

    def stop_display(self, *args, **kwargs):
        return ShowMenuLive.stop_display(self, *args, **kwargs)


def create_back(disp, name):
    """
    Create a MenuTree object to back to the main section
    :param name:
    :return:
    """
    back = ShowMenuTree(disp, ".".join(name))
    back.enter = back.back_quit
    return back



