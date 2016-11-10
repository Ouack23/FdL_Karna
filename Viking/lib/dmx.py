# -*- coding: utf-8 -*-
#
# This file provide DmxThread and other objet to manipulate dmx
#


import threading
import numpy as np
import ola.ClientWrapper
import math

import vthread
import colorconv

from settings import settings
from logger import init_log

log = init_log("dmx")


hist_status = False

def convert_mod(txt=""):
    """
    Convert from modulation file to float
    :param txt:
    :return:
    """
    #log.debug("convert {0}".format(txt))
    if txt == "" or txt is None:
        return 0
    return float(txt)

def exp(x):
    """
    modulation exp
    :param x: value
    :return:
    """
    return math.exp(x*0.6932)-1

def seuil(sens, min, value=None):
    """

    :param sens:
    :param min:
    :param val:
    :return:
    """
    #log.debug("sens {0}, min {1}, val{2}".format(sens, min, val))
    if sens > min:
        if value is None:
            return sens
        else:
            return value

def hist(sens, v_min, value=None, hist_marge=0.15):
    """

    :param sens:
    :param min:
    :param value:
    :param hist_marge:
    :return:
    """
    global hist_status
    if hist_status:
        if sens+hist_marge < v_min:
            hist_status = False
            return 0
        else:
            if value is None:
                return sens
            else:
                return value
    else:
        if sens-hist_marge > v_min:
            hist_status = True
            if value is None:
                return sens
            else:
                return value
        else:
            return 0


def sensors(thmod,s):
        """

        :param s: index sensors
        :return:
        """
        return thmod.thsensors.sensors[s].values.data[0]


class DmxGroup(object):
    """
    This class represent a DMX group
    """

    def __init__(self, hsv_addr, hsv_values, dmx_addr, dmx_output, mod_row, time_row):
        """
        :param hsv_values: HSV values of the lightfile
        :param hsv_addr: addr of the column HSV in the light file
        :param dmx_addr: addr to start the DMX output in RGB
        :param mod_row: modulation row
        :param time_row: absolute time row
        :return:
        """
        self.hsv_values = hsv_values
        self.delta_hsv = np.zeros(3, dtype=np.float32)
        self.delta_rgb = np.zeros(3, dtype=np.float32)
        self.hsv_addr = hsv_addr
        self.dmx_addr = dmx_addr
        self.dmx_output = dmx_output
        self.mod_row = list()
        for row in mod_row:
            row = row[1:]
            for i in range(len(row)):
                row[len(row)-1-i] = row[len(row)-1-i].replace('s[0]','sensors(thmod, 0)')
                if row[len(row)-1-i] == "=":
                    row[len(row)-1-i] = row[len(row)-i]
                elif row[len(row)-1-i] == "=":
                    row[len(row)-1-i] = 0
            self.mod_row.append(row)
        self.time_row = time_row
        self.current_key = 0
        self.sensors = None
        self.n_loop = 0

    def update_dmx(self, frame, global_modulation):
        """

        :param frame: current DMX frame to update
        :param global_modulation: global modulation coef 0..1
        :return:
        """
        global_modulation = 1
        #log.raw("tick frame {2} spot dmx at {0} row {1}".format(self.dmx_addr, self.hsv_values[frame][self.hsv_addr:self.hsv_addr + 3], frame))
        self.dmx_output[self.dmx_addr:self.dmx_addr + 3] = colorconv.conv_hsv_to_rgb(
            self.hsv_values[frame][self.hsv_addr:self.hsv_addr + 3] + global_modulation * self.delta_hsv) + global_modulation * self.delta_rgb * 255


    def update_modulation(self, frame, thmod):
        """
        Update modulation
        :param frame: current frame
        :param thmod: Thread modulation object
        :return:
        """
        if self.sensors is None:
            self.sensors = list()
            for i in range(len(thmod.thsensors.sensors)):
                self.sensors.append(thmod.thsensors.sensors[i].values.data)
        #thmod.clock_thread._set_speed(thmod.thsensors.sensors[0].values.data[0])
        #log.debug("time ref {0}, time key {1}".format(thmod.clock_thread.timeref, self.time_row[self.current_key]))
        if self.current_key+1 >= len(self.time_row) and thmod.clock_thread.timeref > float(self.time_row[-1])*(1+self.n_loop):
            self.n_loop += 1
            log.debug("modulation loop {0}".format(self.n_loop))
            self.current_key = 0
        elif thmod.clock_thread.timeref%float(self.time_row[-1]) > float(self.time_row[self.current_key]):
            self.current_key += 1
            log.debug("enter in key {0}".format(self.current_key))
#        log.debug("mod key {0}".format(self.current_key))

        #log.debug("modulation time {0}, key {1} : {2}".format(thmod.clock_thread.timeref, self.current_key, self.mod_row[0][self.current_key]))
        # if self.mod_row[0][self.current_key] == "" or self.mod_row[0][self.current_key] is None:
        # if self.mod_row[0][self.current_key] == "" or self.mod_row[0][self.current_key] is None:
        #     return
        s = self.sensors
#        log.debug("eval : {0}".format(self.mod_row[i][self.current_key]))
        #eval("log.debug(\"sensor : {0}\".format("+str(self.mod_row[0][self.current_key])+"[0]))")
        #eval('log.debug(\"hello\")')
        for i in range(len(self.delta_hsv)):
            # log.debug(str(s[0]))
            # log.debug(str(s[0][0]))
            # log.debug(str(s[0][0]))
#            exec("log.debug(str("+str(self.mod_row[i][self.current_key][0])+"))")
            #log.debug("self.delta_hsv["+str(i)+"] = float("+str(self.mod_row[i][self.current_key])+"[0])")
            exec("self.delta_hsv["+str(i)+"] = convert_mod("+str(self.mod_row[i][self.current_key])+")") # self.delta_hsv["+str(i)+"] =
        for i in range(len(self.delta_rgb)):
            # log.debug(str(s[0]))
            # log.debug(str(s[0][0]))
            # log.debug(str(s[0][0]))
#            exec("log.debug(str("+str(self.mod_row[i][self.current_key][0])+"))")
            #log.debug("self.delta_hsv["+str(i)+"] = float("+str(self.mod_row[i][self.current_key])+"[0])")
            #log.debug(str(self.mod_row[3+i][self.current_key]))
            exec("self.delta_rgb["+str(i)+"] = convert_mod("+str(self.mod_row[3+i][self.current_key])+")") # self.delta_hsv["+str(i)+"] =
            #pass
        #self.delta_hsv /= 1.0
        #log.debug("delta hsv: {0}, sensors value {1}".format(self.delta_hsv, thmod.thsensors.sensors[0].values.data[0]))
        #log.debug(".")
        #log.debug("update modulation")


class DmxThread(vthread.VikingThread):
    """
    This class represent the DMX thread
    """

    def __init__(self, lightfile, universe=0, dmxoutput_size=255):
        """
        :param lightfile: reference to the lightfile object
        :param universe: DMX universe to use
        :param dmxoutput_size: Output size of the dmx array, reduce to a bit performance improving
        :return:
        """
        vthread.VikingThread.__init__(self, "dmx")
        self.lightfile = lightfile
        self.framerate = int(settings["lightfile"]["framerate"])
        self.clock_thread = None
        self.universe = universe
        self.wrapper = ola.ClientWrapper.ClientWrapper()
        self.client = self.wrapper.Client()
        self.client.SendDmx(self.universe, np.zeros(255, dtype=np.uint8))  # Clean all the universe
        self.dmxout = np.zeros(dmxoutput_size, dtype=np.uint8)
        for spot in lightfile.spots:
            spot.dmx_output = self.dmxout

    def get_current_frame(self):
        """
        This method return the current frame to output
        :return:
        """
        return int(math.ceil(self.clock_thread.timeref*self.framerate)) % len(self.lightfile.frames)

    def do_msg(self, msg):
        """
        Compute all dmx
        :param msg:
        :return:
        """
        #self.log.raw("tick dmx")
        frame = self.get_current_frame()
        for spot in self.lightfile.spots:
            spot.update_dmx(frame, 1)
        #self.log.raw("dmx out put {0}".format(self.dmxout))
        self.client.SendDmx(self.universe, self.dmxout)

    def _on_close(self):
        self.client.SendDmx(self.universe, np.zeros(255, dtype=np.uint8))  # Clean all the universe
