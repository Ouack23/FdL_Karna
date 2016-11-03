# -*- coding: utf-8 -*-
#
# This file provide a card abstraction for display, input, led etc..
#

import time

from settings import settings, VERSION

if settings.get("sys", "raspi"):
    try:
        from Adafruit_ADS1x15.Adafruit_ADS1x15 import ADS1x15
        from Adafruit_LED_Backpack import AlphaNum4
    except ImportError:
        settings["sys"]["raspi"] = False

import ui
import gpio
import sensor
import vthread
import system
import master

from logger import init_log

log = init_log("card")


class CardDriver(object):
    """
    This define all object on the card
    """

    def __init__(self):
        """
        :return:
        """
        if settings.get("sys", "raspi"):
            gpio.init_pigpio()

        self.led = dict()
        self.led["sensors"] = ui.LedDriver(21)#int(settings.get("i/o","led","sensors")))
        self.led["dmx"] = ui.LedDriver(20)#int(settings.get("i/o","led","dmx")))
        self.led["sound"] = ui.LedDriver(16)#int(settings.get("i/o","led","sound")))
        self.led["playing"] = ui.LedDriver(12)#int(settings.get("i/o","led","playing")))
        self.led["status"] = ui.LedDriver(7)#int(settings.get("i/o","led","status")))

        if settings.get("sys", "raspi"):
            self.alphanum4 = AlphaNum4.AlphaNum4()
            self.alphanum4.begin()
            self.alphanum4.set_brightness(int(settings.get("i/o", "display", "bright")))
        else:
            self.alphanum4 = None
        self.display = ui.Display(self.alphanum4, led_status=self.led["status"])

        self.button = dict()
        self.button["right"] = ui.InputDriver("right", self.display.recv_push_right)
        self.button["ok"] = ui.InputDriver("ok", self.display.recv_push_ok)
        self.button["left"] = ui.InputDriver("left", self.display.recv_push_left)
        self.button["reboot"] = ui.InputDriver("reboot")

        if settings.get("sys", "raspi"):
            self.adc = ADS1x15(ic=settings.get("sensor", "model"))  # 16 bit channel
        else:
            self.adc = None
        self.sensor1 = sensor.Sensor(0)
        self.sensor_thread = sensor.SensorThread(self.adc, [self.sensor1, ])

        # self.button["right"].set_fnct_rise(self.display.recv_push_right)
        # self.button["left"].set_fnct_rise(self.display.recv_push_left)
        # self.button["ok"].set_fnct_rise(self.display.recv_push_ok)
        # for button in self.button.values():
        #     button.attach_fnct()

        #self.thread = vthread.VikingThread("ui")

        self.test_output()

        self.init_menu()

    def start_sensor(self, thread_clock):
        """
        Start sensor thread
        :param thread_clock: clock thread for sensor
        :return:
        """
        self.sensor_thread.set_clock(thread_clock)
        self.sensor_thread.start()
        self.sensor_thread.inqueue.put_nowait(vthread.QueueEntry())     # tick to start

    def test_output(self):
        """
        This function test all led, normally used at stratup
        :return:
        """
        for led in self.led.values():
            led.set_on()
        txt = self.display.txt_buffer
        self.display.txt_buffer = "V {:.1f}".format(VERSION)
        self.display.update_display()
        time.sleep(1.5)
        self.display.txt_buffer = "".format(VERSION)
        self.display.update_display()
        for led in self.led.values():
            led.set_off()
        time.sleep(0.5)
        for led in self.led.values():
            led.released()
        self.display.txt_buffer = txt
        self.display.update_display()

    def init_menu(self):
        """
        This function init the menu
        :return:
        """
        mainmenu = ui.ShowMenuTree(self.display, "PLOP")
        showmainmenu = ui.ShowMenuTree(self.display, "")
        capt1menu = ui.ShowMenuTree(self.display, "CAP1")
        capt1_rawtension = ui.ShowMenuTreeLive(self.display, livedisp_rawvoltage, [self.sensor1, ])
        capt1_value = ui.ShowMenuLive(self.display, livedisp_sensorvalue, [self.sensor1, ])
        capt1_direction = ui.ShowMenuStatic(self.display, "WAY{0}".format(settings.get("sensor", "direction")))
        capt1_autominmax_menu = ui.ShowMenuTree(self.display, "AUTO")
        capt1_autominmax = ui.ShowMenuLive(self.display, livedisp_autovoltage, [self.sensor1, ])
        sysmenu = ui.ShowMenuTree(self.display, "SYST")
        poweroff = ui.ShowMenuTree(self.display, "POFF")
        reboot = ui.ShowMenuTree(self.display, "REBT")
        restart = ui.ShowMenuTree(self.display, "REST")
        # capt1_setminmax = ui.ShowMenuTreeLive(self.display, livedisp_rawvoltage, [self.sensor1, ])

        ### mainmenu ###
        mainmenu.elements.append(showmainmenu)
        showmainmenu.elements.append(capt1menu)
        showmainmenu.elements.append(sysmenu)
        showmainmenu.elements.append(ui.create_back(self.display, "HIDE"))
        ### capt1 ###
        # capt1 #
        capt1menu.elements.append(capt1_rawtension)
        capt1menu.elements.append(capt1_autominmax_menu)
        capt1menu.elements.append(capt1_value)
        capt1menu.elements.append(capt1_direction)
        capt1menu.elements.append(ui.create_back(self.display, "MENU"))
        # capt1 -> raw #
        capt1_rawtension.push_left = get_set_sensor_min(self.sensor1)
        capt1_rawtension.push_right = get_set_sensor_max(self.sensor1)
        capt1_rawtension.push_ok = capt1_rawtension.back_quit
        # capt1 -> auto #
        capt1_autominmax.push_ok = change_min_max_auto(capt1_autominmax, self.sensor1)
        capt1_autominmax_menu.elements.append(capt1_autominmax)
        capt1_autominmax_menu.elements.append(ui.create_back(self.display, "CAP1"))
        # capt1 -> value #
        # capt1 -> way #
        capt1_direction.push_ok = change_way(capt1_direction)

        #capt1_value.push_ok = capt1_value.back_quit

        ### sysmenu ###
        # poweroff #
        poweroff.push_ok = system.poweroff
        reboot.push_ok = system.reboot
        restart.push_ok = master.main_exit
        sysmenu.elements.append(poweroff)
        sysmenu.elements.append(reboot)
        sysmenu.elements.append(restart)
        sysmenu.elements.append(ui.create_back(self.display, "MENU"))

        mainmenu.enter()

    def shutdown(self):
        log.debug("shuting down card")
        self.display.current_show.stop_display()
        self.display.txt_buffer = ""
        self.display.update_display()


def get_set_sensor_min(capteur):
    def set_sensor_min():
        capteur.set_min(capteur.raw.data[0])
    return set_sensor_min


def get_set_sensor_max(capteur):
    def set_sensor_max():
        capteur.set_max(capteur.raw.data[0])
    return set_sensor_max


def livedisp_rawvoltage(show, capteur):
    """
    This function show in live the current voltage of the given capteur
    :param show: gave when called (show object)
    :param capteur: capteur object
    :return:
    """
    log.debug("start display raw voltage")
    while not show._stop_thread.is_set():
        show.display.txt_buffer = capteur.raw.data[0]
        show.display.update_display(disp_float=True)
        time.sleep(show._live_dt)


def livedisp_sensorvalue(show, capteur):
    """
    This function show in live the current voltage of the given capteur
    :param show: gave when called (show object)
    :param capteur: capteur object
    :return:
    """
    log.debug("start display sensor value")
    while not show._stop_thread.is_set():
        show.display.txt_buffer = capteur.values.data[0] * 10000
        show.display.update_display(disp_float=True)
        time.sleep(show._live_dt)

def livedisp_autovoltage(show, capteur):
    """
    This function show the current excursion of auto min max
    :param show:
    :param capteur:
    :return:
    """
    log.debug("start display auto voltage")
    show.min = 10000000
    show.max = 0
    while not show._stop_thread.is_set():
        if capteur.raw.data[0] > show.max:
            show.max = capteur.raw.data[0]
        if capteur.raw.data[0] < show.min:
            show.min = capteur.raw.data[0]
        show.display.txt_buffer = show.max-show.min
        show.display.update_display(disp_float=True, decimals=1)
        time.sleep(show._live_dt)


def change_way(menu):
    def change():
        if settings.get("sensor", "direction") == "+":
            settings["sensor"]["direction"] = "-"
            settings.save()
            menu.txt = "WAY-"
            menu.display.update_display()
        else:
            settings["sensor"]["direction"] = "+"
            settings.save()
            menu.txt = "WAY+"
            menu.display.update_display()
    return change


def change_min_max_auto(menu, sensor):
    def change():
        log.debug("Auto set ask by user..")
        sensor.set_min(menu.min)
        sensor.set_max(menu.max)
        menu.stop_display()
        menu.display.current_show.back_quit()
    return change