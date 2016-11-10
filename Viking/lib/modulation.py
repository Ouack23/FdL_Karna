# -*- coding: utf-8 -*-
#
#
# This module provide the modulation thread
#

import vthread
import math

from settings import settings
from logger import init_log

log = init_log("modulation")


class DmxModulationThread(vthread.VikingThread):
    """
    This class define the DMX modulation thread
    """

    def __init__(self, lightfile, thsensors):
        """
        :param lightfile: lightfile object
        :param thsensors: Thread sensor object
        :return:
        """
        vthread.VikingThread.__init__(self, "dmxmod")
        self.lightfile = lightfile
        self.thsensors = thsensors
        self.framerate = int(settings["lightfile"]["framerate"])
        self.clock_thread = None

    def do_msg(self, msg):
        """
        Compute modulation
        :param msg:
        :return:
        """
        # log.debug("do msg mod")
        frame = self.get_current_frame()
        for spot in self.lightfile.spots:
            spot.update_modulation(frame, self)

    def get_current_frame(self):
        """
        This method return the current frame to output
        :return:
        """
        return int(math.ceil(self.clock_thread.timeref*self.framerate)) % len(self.lightfile.frames)





