#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
#

import lib.settings
import time
import os
import random
import math
from ola.ClientWrapper import ClientWrapper

lib.settings.init()

from lib.settings import settings
if settings.get("sys", "raspi"):
    try:
        import pigpio
    except ImportError:
        settings["sys"]["raspi"] = False
#import lib.lightfile as lf
import lib.logger
# import lib.colorconv
# import numpy as np
import lib.vthread
# import lib.system
# import lib.clock
# import lib.dmx
import lib.ui
#import lib.sound
import lib.sensor
import lib.card

import lib.master

import lib.gpio

#import pyo

log = lib.logger.init_log("test")

import lib.scenario


def test_create_lightfile():
    sfile = lib.scenario.ScenarioFile("test2.csv")
    sfile.compute_all_spotgroups()

    sfile.write_lightfile()


def test_read_lightfile():
    lfile = lf.LightFile("test.csv.lf")
    lfile.read()

    universe = 0

    wrapper = ClientWrapper()
    client = wrapper.Client()
    # wrapper.Run()
    log("Start")
    data = np.zeros(len(lfile.frames), dtype=np.uint8)
    for i in range(len(lfile.frames)):
        for j in range(int(settings.get("lightfile", "n_spot"))):
            # log.raw(str(lfile.frames[i][j*3:(j+1)*3]))
            data[j * 3:(j + 1) * 3] = lib.colorconv.conv_hsv_to_rgb(lfile.frames[i][j * 3:(j + 1) * 3])
        data[3:] = 0
        # log.raw("data {0} : ".format(data[0:5]))
        client.SendDmx(universe, data)
        # log.raw(str(np.uint8(lfile.master_dmx[i]*lib.colorconv.conv_hsv_to_rgb(lfile.frames[i]))))
        time.sleep(0.04)
    log("End")


def test_thread():
    th = lib.vthread.VikingThread("test")
    log("..")
    th.start()
    while True:
        e = raw_input("$:")
        if e in ("q", "Q", "quit", "exit"):
            log("ask to exit..")
            lib.system.cleanup()
            break
        else:
            th.inqueue.put(lib.vthread.QueueEntry(e))
    log("out of the loop")


def test_clockthread():
    settings["lightfile"]["framerate"] = 25
    th = lib.clock.ClockThread()
    log("..")
    th.start()
    while True:
        e = raw_input("$:")
        if e in ("q", "Q", "quit", "exit"):
            log("ask to exit..")
            lib.system.cleanup()
            break
        e = e.split(" ")
        if e[0] == "s":
            th._set_speed(float(e[1]))
    log("out of the loop")


def test_clockthread_dmx():
    lfile = lf.LightFile("test.csv.lf")
    lfile.read()
    th = lib.clock.ClockThread()
    th_dmx = lib.dmx.DmxThread(lfile)
    th.set_thread_dmx(th_dmx)
    log("..")
    th.start()
    th_dmx.start()
    while True:
        e = raw_input("$:")
        if e in ("q", "Q", "quit", "exit"):
            log("ask to exit..")
            lib.system.cleanup()
            break
        e = e.split(" ")
        if e[0] == "s":
            th._set_speed(float(e[1]))
    log("out of the loop")


def test_ui():
    disp = lib.ui.Display()
    static = lib.ui.ShowMenuStatic(disp, "HOWD")
    static2 = lib.ui.ShowMenuStatic(disp, "PLOP")
    back = lib.ui.ShowMenuTree(disp, "<---")
    back.enter = back.back_quit
    menu = lib.ui.ShowMenuTree(disp, "    ")
    menu.elements.append(static)
    menu.elements.append(static2)
    submenu = lib.ui.ShowMenuTree(disp, "SUBM")
    sta = lib.ui.ShowMenuStatic(disp, "AAAA")
    stb = lib.ui.ShowMenuStatic(disp, "BBBB")
    submenu.elements.append(sta)
    submenu.elements.append(stb)
    submenu.elements.append(back)
    menu.elements.append(submenu)
    menu.elements.append(back)

    menu.enter()
    disp.recv_push_right()
    disp.recv_push_right()
    disp.recv_push_ok()
    disp.recv_push_right()
    disp.recv_push_left()
    disp.recv_push_left()

    disp.recv_push_ok()
    disp.recv_push_left()


def test_sound_table():

    sound = lib.sound.SoundFile(os.path.join(settings.get_path("sound"), "ocean.wav"))
    player = pyo.TableRead(sound)
    player.out()


def test_sensor():
    N_entry = 30
    Min = 1.1
    Max = 1.15
    Amplitude = (Max-Min*1.1)/2.0
    Mid = Min + (Max-Min)/float(2)
    def calc_value():
        v = random.random()*2*3.15
        v = Mid + math.cos(v)*Amplitude
        print(v)
        return v
    #values = np.zeros(N_entry, dtype=np.float32)
    sensor = lib.sensor.Sensor(0, lib.sensor.SVCAvg, (4, ))
    sensor.v_min = Min
    sensor.v_max = Max
    for i in range(N_entry):
        sensor.add_value(calc_value())
    print(sensor.buffer.data)
    print(sensor.values.data)


def test_card():
    card = lib.card.CardDriver()


def test_input():
    def input_pressed(name):
        def fnct(*args):
            log.info("{0} pressed".format(name))
        return fnct
    lib.gpio.init_pigpio()
    buttons = ["ok","left","right","reboot"]
    for button in buttons:
        log.debug("init {0} at {1}".format(button, settings.get("i/o", "button", button)))
        lib.gpio.rpi.set_mode(settings.get("i/o", "button", button), pigpio.INPUT)
        lib.gpio.rpi.set_pull_up_down(settings.get("i/o", "button", button), pigpio.PUD_UP)
        if button != "reboot":
            lib.gpio.rpi.set_glitch_filter(settings.get("i/o", "button", button), 500)
        else:
            lib.gpio.rpi.set_glitch_filter(settings.get("i/o", "button", button), 3000)
        lib.gpio.rpi.callback(settings.get("i/o", "button", button), pigpio.FALLING_EDGE, input_pressed(button))


def test_master():
    lib.master.main_init()
    lib.master.main_start_clock()
    # try:
    #     input("Enter to quit")
    # except:
    #     pass
    if not settings.get("sys", "raspi"):
        lib.master.emulate_input()
    else:
        try:
            input("Enter to quit")
        except:
            pass
    lib.master.main_exit()


# test_create_lightfile()
# test_read_lightfile()

# test_thread()
# test_clockthread()

# test_clockthread_dmx()

# test_ui()

#test_sensor()

#test_card()


# test_input()

test_master()

# try:
#     input("Enter to quit")
# except:
#     pass

#lib.vthread.quit_all_threads()

#
# import csv
#
# lightfile = list()
#
# with open('test.csv', 'rb') as csvfile:
#     lf_reader = csv.reader(csvfile, delimiter=',')
#     for row in lf_reader:
#         lightfile.append(row)
#
#
# for row in lightfile:
#     print(",".join(row))
#
# log.debug("Test debug log message")
#
# spot = lf.LF_SpotGroup(lightfile[3], lightfile[1])
# spot.solve_color(lightfile[3])
# spot.solve_parameters(lightfile[4:10])
#
# print(str(spot.frames))


# for frame in spot.frames:
#    print(frame.rgb)
