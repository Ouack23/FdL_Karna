from __future__ import print_function
import logging
from ola.DMXConstants import DMX_MIN_SLOT_VALUE, DMX_MAX_SLOT_VALUE, DMX_UNIVERSE_SIZE
import sys
from array import array
import math
from ola.ClientWrapper import ClientWrapper


class DMX(object):
    def __init__(self, universe, duration=0, channels=DMX_UNIVERSE_SIZE):
        logging.info("DMX Initialization")

        self._universe = universe
        self._duration = duration
        self._channels = channels
        self._wrapper = ClientWrapper()
        self._client = self._wrapper.Client()

    def set_duration(self, value):
        self._duration = value

    def send_dmx(self, data):
        logging.debug("I'm in send_dmx()")
        self._client.SendDmx(self._universe, data, self.dmx_sent)

    @staticmethod
    def dmx_sent(status):
        if status.Succeeded():
            logging.debug('DMX sent successfully !')
        else:
            logging.warning('Error : %s' % status.message, file=sys.stderr)

    def run_dmx(self):
        logging.info("Run DMX")

        if self._duration != 0:
            self._wrapper.AddEvent(self._duration, self.stop)
            logging.info("Running for " + str(self._duration) + " ms !")

        else:
            logging.info("Running indefinitely ! ")

        self._wrapper.Run()

    def stop(self):
        self._wrapper.Stop()
        logging.info("Stopped !")
