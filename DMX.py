from __future__ import print_function
from ola.DMXConstants import DMX_MIN_SLOT_VALUE, DMX_MAX_SLOT_VALUE, DMX_UNIVERSE_SIZE
import sys
from array import array
from log import log, logSection
import math

class DMX(object):
    def __init__(self, universe, client_wrapper=None, duration=0, channels=DMX_UNIVERSE_SIZE):
        logSection("Initialization")

        self._universe = universe
        self._wrapper = client_wrapper
        self._client = client_wrapper.Client()
        self._duration = duration;
        self._update_interval = 0
        self._update_number = 0
        self._current_iteration = 0
        self._channels = channels

        init_DMX_array = array('B')

        for i in range(min(self._channels, DMX_UNIVERSE_SIZE)):
            init_DMX_array.append(DMX_MIN_SLOT_VALUE)

        self._step = init_DMX_array
        self._data_current = init_DMX_array
        self._data_begin = init_DMX_array
        self._data_end = init_DMX_array

        if self._wrapper:
            print("Stopping previous wrapper")
            self.Stop()


    def set_duration(self, value):
        self._duration = value


    def FadeDMX(self, data_begin, data_end, update_interval):
        logSection("FadeDMX")

        if len(data_begin) != len(data_end):
            print("Error : Not same size for begin ("+str(len(data_begin))+") and end ("+str(len(data_end))+") DMX data values")

        elif update_interval <= 0:
            print("Error : Wrong update interval value ("+str(update_interval)+")")

        elif data_begin == data_end:
            print("Error : Cannot make a fade between two similar DMX data (useless) !")

        else:
            self._data_begin = data_begin
            self._data_current = data_begin
            self._data_end = data_end
            self._update_interval = update_interval
            self.calculUpdateNumber()
            self.calculStep()

            log(self._data_begin, "Initial Data")
            log(self._data_current, "Current Data")
            log(self._data_end, "Final Data")
            log(self._update_interval, "Update Interval")
            log(self._update_number, "Number of Updates")
            log(self._duration, "Duration")
            log(self._step, "Step at each update")

            if self._step == 0:
                print("Erreur : step = 0 !")
                return False

            else:
                self.FadeDMX_callback()
                return True

    def FadeDMX_callback(self):
        logSection("FadeDMX Iteration")

        self._current_iteration += 1
        log(self._current_iteration, "Current Iteration")

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

        log(self._data_current, "Current Data Monitoring")

        self.SendDMX(self._data_current)
        self._wrapper.AddEvent(self._update_interval, self.FadeDMX_callback)


    def calculStep(self):
        for i in range(self._channels):
            if(self._data_begin[i] != self._data_end[i]):
                step = abs(self._data_end[i] - self._data_begin[i])
                step = step / self._update_number

                if step < 1 and self._update_interval < (int)(self._update_interval / step):
                    self._update_interval = (int)(self._update_interval / step)
                    self._step[i] = 1

                else:
                    self._step[i] = (int)(step)


    def calculUpdateNumber(self):
        update_number = (float)(self._duration) / (float)(self._update_interval)

        if update_number != 0 and update_number < 1:
            self._update_number = 1

        else:
            self._update_number = math.floor(update_number)


    def SendDMX(self, data):
        self._client.SendDmx(self._universe, data, self.DMXSent)


    def DMXSent(self, status):
        if status.Succeeded():
            print('DMX sent successfully !')
        else:
            print('Error : %s' % status.message, file=sys.stderr)


    def Run(self):
        logSection("Run")

        if self._duration != 0:
            self._wrapper.AddEvent(self._duration, self.Stop)
            print("Running for " + str(self._duration) + " ms !")

        else:
            print("Running indefinitly ! ")

        if self._wrapper:
            self._wrapper.Run()


    def Stop(self):
        logSection("Stop")

        self._wrapper.Stop()
        print("Stopped !")