import logging
from ola.DMXConstants import DMX_MIN_SLOT_VALUE, DMX_MAX_SLOT_VALUE, DMX_UNIVERSE_SIZE
import sys
import ola
from ola.ClientWrapper import ClientWrapper
from twisted.internet import threads
from array import array
import os
import math

wrapper = None


def run_wrapper():
    global wrapper
    wrapper.Run()


def set_wrapper():
    global wrapper
    try:
        wrapper = ClientWrapper()
    except ola.OlaClient.OLADNotRunningException:
        logging.error("OLA is not running !")
        os.system("olad -f")
        os.system("sleep 1")
        os.system("ola_patch -d 1 -p 0 -u 0")
        wrapper = ClientWrapper()

    return wrapper


def stop_wrapper():
    global wrapper
    wrapper.Stop()
    logging.info("Stopped !")


def dmx_sent(status):
    if status.Succeeded():
        logging.debug('DMX sent successfully !')
    else:
        logging.error(status.message)


def array_to_string(tab):
    result = "["
    
    for i in range(len(tab) - 1):
        result += str(tab[i]) + ", "
        
    result += str(tab[len(tab) - 1]) + "]"
    
    return result
        

class DMX(object):
    def __init__(self, universe, duration=0, channels=DMX_UNIVERSE_SIZE):
        logging.info("DMX Initialization")

        self._universe = universe
        self._duration = duration
        self._channels = channels
        self._update = 0
        self._update_number = 0
        self._current_iteration = 0

        init_dmx_array = self.get_default_dmx_array()

        self._step = init_dmx_array
        self._data_current = init_dmx_array
        self._data_begin = init_dmx_array
        self._data_end = init_dmx_array

        logging.info("Running DMX thread indefinitely")
        self._state = threads.deferToThread(set_wrapper)

    def set_duration(self, value):
        self._duration = value

    def send_dmx(self, data):
        global wrapper
        set_wrapper()
        wrapper.Client().SendDmx(self._universe, data, dmx_sent)
        logging.info("Sending DMX data : " + array_to_string(data))
        logging.info("Running for " + str(self._duration) + " s !")
        wrapper.AddEvent(self.get_duration_ms(), stop_wrapper)
        run_wrapper()

    def get_default_dmx_array(self):
        default_dmx_array = array('B')

        logging.debug("Initializing DMX arrays with size " + str(min(self._channels, DMX_UNIVERSE_SIZE)))

        for i in range(min(self._channels, DMX_UNIVERSE_SIZE)):
            default_dmx_array.append(DMX_MIN_SLOT_VALUE)

        return default_dmx_array

    def get_default_float_array(self):
        default_float_array = array('d')

        for i in range(min(self._channels, DMX_UNIVERSE_SIZE)):
            default_float_array.append(DMX_MIN_SLOT_VALUE)

        return default_float_array

    def send_fade_dmx(self, data_begin, data_end):
        global wrapper
        logging.debug("I'm in send_fade_dmx()")

        if len(data_begin) != len(data_end):
            logging.error("Error : Not same size for begin ("+str(len(data_begin))+") and end ("+str(len(data_end))+") DMX data values")

        elif data_begin == data_end:
            logging.error("Error : Cannot make a fade between two similar DMX data (useless) !")

        else:
            self._data_begin = data_begin
            self._data_current = data_begin
            self._data_end = data_end
            self._update_number = self.get_update_number()
            self._update = self.calcul_update_ms()
            self._step = self.calcul_step()
            self._duration = self.get_real_duration_ms()

            logging.info("Initial Data :           " + array_to_string(self._data_begin))
            logging.debug("Current Data :           " + array_to_string(self._data_current))
            logging.info("Final Data :             " + array_to_string(self._data_end))
            logging.info("Duration :               " + str(self._duration) + " ms")
            logging.info("Step at each update :    " + array_to_string(self._step))
            logging.info("Update each :            " + str(self._update) + " ms")

            wrapper.AddEvent(self._duration, stop_wrapper)
            wrapper.AddEvent(self._update, self.fade_dmx_callback)
            run_wrapper()

    def fade_dmx_callback(self):
        global wrapper

        self._current_iteration += 1
        if self._current_iteration <= self._update_number:
            logging.debug("Current Iteration : " + str(self._current_iteration))

            for i in range(self._channels):
                if abs(self._data_end[i] - self._data_current[i]) < self._step[i]:
                    self._data_current[i] = self._data_end[i]
                else:
                    if self._data_current[i] < self._data_end[i]:
                        self._data_current[i] += self._step[i]

                    elif self._data_current[i] > self._data_end[i]:
                        self._data_current[i] -= self._step[i]

            logging.debug("Current Data Monitoring : " + array_to_string(self._data_current))

            wrapper.Client().SendDmx(self._universe, self._data_current, dmx_sent)
            wrapper.AddEvent(self._update, self.fade_dmx_callback)

    def calcul_step(self):
        step_f = self.get_default_float_array()
        step_i = self.get_default_dmx_array()

        for i in range(self._channels):
            if self._data_begin[i] != self._data_end[i]:
                step_f[i] = abs(self._data_end[i] - self._data_begin[i])
                step_f[i] /= self.get_update_number()

                if step_f[i] < 1:
                    logging.warning("Step < 1 ! setting to 1 anyway")
                    step_i[i] = 1
                else:
                    step_i[i] = int(step_f[i])

        return step_i

    def get_duration_ms(self):
        return self._duration * 1000

    def get_update_number(self):
        nb_update_max = 0

        for i in range(self._channels):
            diff = abs(self._data_end[i] - self._data_begin[i])
            if nb_update_max < diff:
                nb_update_max = diff

        return nb_update_max

    def calcul_update_ms(self):
        return math.ceil(self.get_duration_ms() / self.get_update_number())

    def get_real_duration_ms(self):
        return self._update * self.get_update_number() + 200
