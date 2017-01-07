from DMX import DMX
import logging
from ola.DMXConstants import DMX_MIN_SLOT_VALUE, DMX_MAX_SLOT_VALUE, DMX_UNIVERSE_SIZE
from array import array
import math


class DMXFade(DMX):
    def __init__(self, universe, duration=0, channels=DMX_UNIVERSE_SIZE):
        logging.info("DMX Fade Initialization")
        DMX.__init__(self, universe, duration, channels)

        self._update_interval = 0
        self._update_number = 0
        self._current_iteration = 0

        init_dmx_array = self.get_default_dmx_array()

        self._step = init_dmx_array
        self._data_current = init_dmx_array
        self._data_begin = init_dmx_array
        self._data_end = init_dmx_array

    def get_default_dmx_array(self):
        default_dmx_array = array('B')

        logging.debug("Initializing DMX arrays with size " + str(min(self._channels, DMX_UNIVERSE_SIZE)))

        for i in range(min(self._channels, DMX_UNIVERSE_SIZE)):
            default_dmx_array.append(DMX_MIN_SLOT_VALUE)

        return default_dmx_array

    def fade_dmx(self, data_begin, data_end, update_interval):
        logging.info("FadeDMX")

        if len(data_begin) != len(data_end):
            logging.error("Error : Not same size for begin ("+str(len(data_begin))+") and end ("+str(len(data_end))+") DMX data values")

        elif update_interval <= 0:
            logging.error("Error : Wrong update interval value ("+str(update_interval)+")")

        elif data_begin == data_end:
            logging.error("Error : Cannot make a fade between two similar DMX data (useless) !")

        else:
            self._data_begin = data_begin
            self._data_current = data_begin
            self._data_end = data_end
            self._update_interval = update_interval
            self.calcul_update_number()
            self.calcul_step()

            logging.debug("Initial Data : " + str(self._data_begin))
            logging.debug("Current Data : " + str(self._data_current))
            logging.debug("Final Data : " + str(self._data_end))
            logging.debug("Update Interval : " + str(self._update_interval))
            logging.debug( "Number of Updates : " + str(self._update_number))
            logging.debug("Duration : " + str(self._duration))
            logging.debug("Step at each update : " + str(self._step))

            if self._step == 0:
                logging.warning("Error : step = 0 !")
                return False

            else:
                self._wrapper.AddEvent(self._duration, self.stop)
                self.fade_dmx_callback()
                self._wrapper.Run()
                return True

    def fade_dmx_callback(self):
        logging.info("FadeDMX Iteration")

        self._current_iteration += 1
        logging.debug("Current Iteration : " + str(self._current_iteration))

        for i in range(self._channels):
            if self._update_number == 1:
                self._data_current[i] = self._data_end[i]

            if self._current_iteration == self._update_number:
                self._data_current[i] = self._data_end[i]

            else:
                if self._data_current[i] < self._data_end[i]:
                    self._data_current[i] += self._step[i]

                elif self._data_current[i] > self._data_end[i]:
                    self._data_current[i] -= self._step[i]

        logging.debug("Current Data Monitoring : " + str(self._data_current))

        self.send_dmx(self._data_current)
        self._wrapper.AddEvent(self._update_interval, self.fade_dmx_callback)

    def calcul_step(self):
        for i in range(self._channels):
            if self._data_begin[i] != self._data_end[i]:
                step = abs(self._data_end[i] - self._data_begin[i])
                step /= self._update_number

                if step < 1 and self._update_interval < int(self._update_interval / step):
                    self._update_interval = int(self._update_interval / step)
                    self._step[i] = 1

                else:
                    self._step[i] = int(step)

    def calcul_update_number(self):
        update_number = float(self._duration) / float(self._update_interval)

        if update_number < 1:
            self._update_number = 1

        else:
            self._update_number = math.floor(update_number)