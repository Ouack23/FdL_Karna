# -*- coding: utf-8 -*-
#
# This file load settings and can modify them
#   Settings are store in a JSON file
#

import sys
import os
import json
# Import log #
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import lib.logger as logger
#
log = logger.init_log("setting", settings={"log": dict()}, log_type="Console")


VERSION = 1.0

settings = None

_DEFAULT_SETTING = dict()
_DEFAULT_SETTING["log"] = dict()
_DEFAULT_SETTING["log"]["level"] = "raw"
_DEFAULT_SETTING["log"]["output"] = "Console"

_DEFAULT_SETTING["sys"] = dict()
_DEFAULT_SETTING["sys"]["exit_on_error"] = True
_DEFAULT_SETTING["sys"]["default"] = dict()
_DEFAULT_SETTING["sys"]["default"]["queue_size"] = 100
_DEFAULT_SETTING["sys"]["raspi"] = True

_DEFAULT_SETTING["scenario"] = dict()
_DEFAULT_SETTING["scenario"]["delimiter"] = str(",")
_DEFAULT_SETTING["scenario"]["framerate"] = 25
_DEFAULT_SETTING["scenario"]["start_spotdata"] = 8
_DEFAULT_SETTING["scenario"]["spotdata_lines"] = 13 # color R G B H S V dH dS dV dR dG dB

_DEFAULT_SETTING["sensor"] = dict()
_DEFAULT_SETTING["sensor"]["buffer_size"] = 50
_DEFAULT_SETTING["sensor"]["model"] = 0x01
_DEFAULT_SETTING["sensor"]["gain"] = 2048
_DEFAULT_SETTING["sensor"]["sps"] = 16
_DEFAULT_SETTING["sensor"]["automin"] = True
_DEFAULT_SETTING["sensor"]["automax"] = True
_DEFAULT_SETTING["sensor"]["v_min"] = 1199.68
_DEFAULT_SETTING["sensor"]["v_max"] = 1204.5
_DEFAULT_SETTING["sensor"]["timecompressor"] = 2
_DEFAULT_SETTING["sensor"]["compressor"] = 0.009
_DEFAULT_SETTING["sensor"]["average"] = 25
_DEFAULT_SETTING["sensor"]["avgpower"] = 1.2
_DEFAULT_SETTING["sensor"]["direction"] = "+"

_DEFAULT_SETTING["i/o"] = dict()
_DEFAULT_SETTING["i/o"]["bouncetime"] = 300
_DEFAULT_SETTING["i/o"]["led"] = dict()
_DEFAULT_SETTING["i/o"]["led"]["sensors"] = 21  # 40
_DEFAULT_SETTING["i/o"]["led"]["dmx"] = 20      # 38
_DEFAULT_SETTING["i/o"]["led"]["sound"] = 16    # 36
_DEFAULT_SETTING["i/o"]["led"]["playing"] = 12  # 32
_DEFAULT_SETTING["i/o"]["led"]["status"] = 7    # 26
_DEFAULT_SETTING["i/o"]["button"] = dict()
_DEFAULT_SETTING["i/o"]["button"]["right"] = 19  # 31
_DEFAULT_SETTING["i/o"]["button"]["ok"] = 13    # 33
_DEFAULT_SETTING["i/o"]["button"]["left"] = 6  # 35
_DEFAULT_SETTING["i/o"]["button"]["reboot"] = 26    # 37
_DEFAULT_SETTING["i/o"]["display"] = dict()
_DEFAULT_SETTING["i/o"]["display"]["framerate"] = 10
_DEFAULT_SETTING["i/o"]["display"]["len"] = 4
_DEFAULT_SETTING["i/o"]["display"]["bright"] = 1


_DEFAULT_SETTING["lightfile"] = dict()
_DEFAULT_SETTING["lightfile"]["name"] = "test2.csv.lf"
_DEFAULT_SETTING["lightfile"]["framerate"] = 25

_DEFAULT_SETTING["path"] = dict()
_DEFAULT_SETTING["path"]["main"] = "/media/Donnees/Karnaval/BouclierViking/"
_DEFAULT_SETTING["path"]["relative"] = dict()
_DEFAULT_SETTING["path"]["relative"]["sound"] = "media"

_DEFAULT_SETTING["uart"] = dict()
_DEFAULT_SETTING["uart"]["port"] = "/dev/ttyATH0"
_DEFAULT_SETTING["uart"]["baudrate"] = 9600
_DEFAULT_SETTING["uart"]["timeout"] = 1
_DEFAULT_SETTING["uart"]["size"] = 4       # 4 = 1 float


class Settings(dict):
    """
    This class old settings
    """

    def __init__(self, path, default=dict()):
        """
        :param path: path to the settings file
        :return:
        """
        self._path = path
        self._default = default
        dict.__init__(self, default)
        try:
            with open(path, 'r') as fp:
                try:
                    self.update(json.load(fp))
                except:
                    log.error("Could not load settings")
        except IOError:
            log.info("No settings found at path {0}, create one".format(path))
            if default != {}:                       # If there is some default settings
                try:
                    with open(path, 'wr') as fp:    # Create setting file
                        pass
                    self.save()                     # Write settings on disk
                except (IOError, OSError) as e:
                    log.error("Could not create defauflt setting file, skip")
        except json.scanner.JSONDecodeError as e:
            log.error("Could not load settings : {0}".format(e))

    def save(self):
        return self._save(self._path, "w")

    def save_as(self, path):
        return self._save(path, "a")

    def _save(self, path, mode):
        with open(path, mode) as fp:
            json.dump(self, fp)

    def __getitem__(self, item):
        if item not in self.keys():
            return self._default[item]
        return dict.__getitem__(self, item)

    def get_default(self, *args):
        """
        Return the default value, act as get but for the default dictionnarie
        :param args:
        :return:
        """
        d = self._default
        for elem in args:
            d = d[elem]
        return d

    def get(self, *args):
        """
        Return the correct value
        :param args: path to the setting (ex: ("OSC", "ackport"))
        :return:
        """
        d = self
        for elem in args:
            if elem in d.keys():
                d = d[elem]
            else:
                return self.get_default(*args)
        return d

    def get_path(self, *args):
        """
        This function return a path based on settings with ("path","main") as root path
        :param args: each relative path to cross
        :return:
        """
        if args[0] not in self.get("path", "relative").keys():
            return self.get("path", *args)
        abs_path = self.get("path", "main")
        for path in args:
            abs_path = os.path.join(abs_path, settings.get("path", "relative", path))
        return abs_path



def init(settings_path=None, default_settings=None):
    """
    This function initialized setting module
    :param settings_path: path to the setting JSON file
    :type settings_path: str
    :param default_settings: default settings used if JSON file don't define them
    :type default_settings: dict
    :return: None
    """
    global settings
    if settings_path is None:
        settings_path = os.path.expanduser("~/.viking.conf")
    if default_settings is None:
        default_settings = _DEFAULT_SETTING
    settings = Settings(settings_path, default_settings)
    logger.SETTINGS = settings
    log.debug(settings)
