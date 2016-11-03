# -*- coding: utf-8 -*-
#
# This file provide sensor interface
#

import time

import numpy as np

import mtools
import system
import vthread

from settings import settings
from logger import init_log

log = init_log("sensor")


class SensorValueCalc(object):
    """
    This class provide a calculator model for Sensor
    """

    def __init__(self, sensor):
        """
        :param sensor: Sensor object
        :return:
        """
        self.sensor = sensor

    def __call__(self, *args, **kwargs):
        pass


class SVCAvg(SensorValueCalc):
    """
    Calculator with average
    """

    def __init__(self, sensor, avg, power=1):
        """
        :param sensor: Sensor object
        :param avg: Average depth 1 ==> current value + 1
        :param power: average strength
        :return:
        """
        SensorValueCalc.__init__(self, sensor)
        if avg >= settings.get("sensor", "buffer_size"):
            system.error_can_exit("Average can't be greeter or equal to the sensor buffer size")
        self.avg = avg + 1
        self.avg_div = 0
        self.avg_vector = np.zeros(self.avg, dtype=np.float32)
        for i in range(self.avg):  # = 1 + 1/2 + 1/3 + 1/4
            self.avg_vector[i] = 1 / float(i * power + 1)
        self.avg_div = float(np.sum(self.avg_vector))

    def __call__(self):
        """
        This function calculate the sensor value
        :return:
        """
        if settings.get("sensor", "direction") == "+":
            self.sensor.values.put(np.sum(self.avg_vector * self.sensor.buffer.data[0:self.avg]) / self.avg_div)
        else:
            self.sensor.values.put(1-np.sum(self.avg_vector * self.sensor.buffer.data[0:self.avg]) / self.avg_div)


class Sensor(object):
    """
    This class define a sensor
    """

    def __init__(self, adc_channel, calc=SVCAvg, calc_args=None):
        """
        :param adc_channel:
        :param calc: Calculator class
        :param calc_args: Calculator arguments
        :return:
        """
        adc_channel = int(adc_channel)
        if adc_channel < 0 or adc_channel > 3:
            system.error_can_exit("ADC channel must be in [0,3]")
        self.adc_channel = adc_channel
        self.gain = settings.get("sensor", "gain")
        self.buffer = mtools.CircularBuffer(settings.get("sensor", "buffer_size"))
        self.raw = mtools.CircularBuffer(settings.get("sensor", "buffer_size"))
        self.values = mtools.CircularBuffer(settings.get("sensor", "buffer_size"))
        self.v_min = float(settings.get("sensor", "v_min"))  # 0
        self.v_max = float(settings.get("sensor", "v_max"))  # 0.1 avoid zero div
        self.calculator = None
        if calc_args is None:
            calc_args = [int(settings.get("sensor", "average")), float(settings.get("sensor", "avgpower"))]
        self.set_calculator(calc, calc_args)
        self.clock = None
        self._time_compressor = float(settings.get("sensor", "timecompressor"))
        self._framerate = 1/float(settings.get("lightfile", "framerate"))
        self._compressor = float(settings.get("sensor", "compressor"))
        self._lastcompress = 0

    def set_min(self, value):
        """
        Set sensor min value
        :param value:
        :return:
        """
        log.debug("Set min value {0}".format(value))
        self.v_min = float(value)
        settings["sensor"]["v_min"] = float(value)
        settings.save()

    def set_max(self, value):
        """
        Set sensor min value
        :param value:
        :return:
        """
        log.debug("Set max value {0}".format(value))
        self.v_max = float(value)
        settings["sensor"]["v_max"] = float(value)
        settings.save()

    def set_calculator(self, calc=SVCAvg, calc_args=list()):
        """
        Set the calculator
        :param calc: Calculator class
        :param calc_args: Calculator arguments
        :return:
        """
        self.calculator = calc(self, *calc_args)

    def add_value(self, value):
        """
        Add the value in the buffer and calculate the value
        :param value:
        :return:
        """
        value = float(value)
        if settings.get("sensor", "automin"):
            if value < self.v_min or value > self.v_max:
                if settings.get("sensor", "direction") == "+":
                    log.info("auto set min : {0}->{1}".format(self.v_min, value))
                    self.set_min(value)
                else:
                    log.info("auto set max : {0}->{1}".format(self.v_max, value))
                    self.set_max(value)
            elif self.clock.timeref-self._lastcompress > self._time_compressor :
                if settings.get("sensor", "direction") == "+":
                    log.debug("capteur {3} :: min compression : {0} : {1} -> {2}".format((self.v_max - self.v_min) * 0.01, self.v_min, self.v_min+(self.v_max - self.v_min) * 0.01, self.values.data[0]))
                    self.v_min += (self.v_max - self.v_min) * self._compressor * self._time_compressor
                else:
                    log.debug("capteur {3} :: max compression : {0} : {1} -> {2}".format((self.v_max - self.v_min) * 0.01, self.v_max, self.v_max-(self.v_max - self.v_min) * 0.01, self.values.data[0]))
                    self.v_max -= (self.v_max - self.v_min) * self._compressor * self._time_compressor
                self._lastcompress = self.clock.timeref
        # if settings.get("sensor", "automax"):
        #     if value > self.v_max:
        #         log.info("auto set max : {0}->{1}".format(self.v_max, value))
        #         self.set_max(value)
        #     elif self.clock.timeref%self._time_compressor < 2*self._framerate :
        #         log.debug("max compression : {0} : {1} -> {2}".format((self.v_max - self.v_min) * 0.01, self.v_max, self.v_max+(self.v_max - self.v_min) * 0.01))
        #         self.v_max -= (self.v_max - self.v_min) * 0.005
        # log.debug("Add value in sensor : {0}".format(value))
        # Add raw value
        if self.v_min == self.v_max:
            log.warning("MIN = MAX !")
            return
        self.raw.put(value)
        # Add value in [0;1]
        self.buffer.put((max(min(value, self.v_max), self.v_min) - self.v_min) / (self.v_max - self.v_min))
        # Add computed value
        self.calculator()  # Compute the value
        # log.debug("Add value in sensor : {0} :: {1} :: {2}".format(value, (
        #     max(min(value, self.v_max), self.v_min) - self.v_min) / float(self.v_max - self.v_min), self.values.data[0]))
        # log.debug(self.values.data)


class SensorThread(vthread.VikingThread):
    """
    This thread read ADC sensors values and update them
    """

    def __init__(self, adc, sensors):
        """
        :param adc: adc object
        :param sensors:
        :return:
        """
        vthread.VikingThread.__init__(self, "sensors")
        self.adc = adc
        self.sensors = sensors
        self.sps = settings.get("sensor", "sps")

    def do_msg(self, msg):
        """
        :param msg:
        :return:
        """
        if not settings.get("sys", "raspi"):
            time.sleep(1)
        else:
            for sensor in self.sensors:
                sensor.add_value(self.adc.readADCSingleEnded(sensor.adc_channel, sensor.gain, self.sps))
        time.sleep(1/50.0)
        self.inqueue.put_nowait(msg)

    def set_clock(self, clock):
        """
        Set thread clock
        :param clock: Thread clock
        :return:
        """
        for sensor in self.sensors:
            sensor.clock = clock