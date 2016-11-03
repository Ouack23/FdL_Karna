# -*- coding: utf-8 -*-
#
# This file provide the clock thread
#


import threading
import vthread
import os
import time

import system

from settings import settings
from logger import init_log
log = init_log("clock")


class ClockThread(vthread.VikingThread):
    """
    This class describe the clock (or sync) thread
    """

    tick = vthread.QueueEntry()

    def __init__(self):
        vthread.VikingThread.__init__(self, "clock")
        self._time = 0
        self.timeref = float(0)
        self.timeref_lock = threading.Lock()
        self.speedref = 1
        self.speed_lock = threading.Lock()
        self.framerate = float(settings["lightfile"]["framerate"])
        self.tickinteral = float(1)/self.framerate
        self.th_sound = None
        self.th_dmx = None
        self.th_dmxmod = None
        self.th_soundmod = None

    @staticmethod
    def _get_monotonic_time():
        """
        This method return the monotonic time
        :return:
        """
        return os.times()[4]

    def _update_timeref(self):
        """
        This function update the time ref
        :return:
        """
        with self.timeref_lock:
            _time = ClockThread._get_monotonic_time()      # Get monotonic time
            self.timeref += self.speedref * (_time - self._time)
            self._time = _time

    def _set_speed(self, speed):
        """
        :param speed: speed
        :return:
        """
        with self.speed_lock:
            self._update_timeref()      # Update time ref to count time elapsed with the old speed ref
            self.speedref = speed

    def get_speed(self):
        """
        This method return the current speed
        :param speed:
        :return:
        """
        with self.speed_lock:
            return self.speedref

    def _on_start(self):
        """
        This method is called on startup and used for setting the first time
        :return:
        """
        #if None in (self.th_dmx, self.th_dmxmod, self.th_sound, self.th_soundmod):
        if None in (self.th_dmx, ):
            self.log.error("Threads dmx, dmxmod, sound and soundmod must be givent to clock before starting it")
            system.exit_on_error()
        self._time = ClockThread._get_monotonic_time()
        self.inqueue.put(ClockThread.tick)      # Add a time tick

    def _sleep_until_next(self):
        """
        This method sleep until next
        :return:
        """
        # with self.timeref_lock:
        #     log.debug("speed_lock WAIT")
        #     with self.speed_lock:
        #         log.debug("speed_lock IN")
        dt = ClockThread._get_monotonic_time() - self._time
        if dt > self.tickinteral:
            self.log.warning("/!\ Timeinterval to short")
        else:
            time.sleep(self.tickinteral-dt)
        self.inqueue.put(ClockThread.tick)
            # log.debug("speed_lock OUT")

    def _set_clock_thread(self, th):
        """
        This method set the clock on a thread
        :param th: thread
        :return:
        """
        th.clock_thread = self

    def set_thread_dmx(self, dmxth):
        """
        Set the dmx thread
        :param dmxth: DMX thread
        :return:
        """
        self.th_dmx = dmxth
        self._set_clock_thread(dmxth)

    def set_thread_dmxmod(self, dmxmodth):
        """
        Set the dmx thread
        :param dmxmodth: DMX modulation thread
        :return:
        """
        self.th_dmxmod = dmxmodth
        self._set_clock_thread(dmxmodth)

    def do_msg(self, msg):
        """
        Time tick function
        :return:
        """
        self._update_timeref()
        self.th_dmx.inqueue.put(ClockThread.tick)
        self.th_dmxmod.inqueue.put(ClockThread.tick)
        # self.log("Tick at {0} time {1}".format(ClockThread._get_monotonic_time(), self.timeref))
        self._sleep_until_next()





