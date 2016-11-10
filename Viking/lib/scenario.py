# -*- coding: utf-8 -*-
#
# This file provide an interface with the scenario files
#

from lib.settings import settings
import lightfile
import lib.logger

log = lib.logger.init_log("scenario")

import csv
import math


class ScenarioFile(object):
    """
    This class represent a scenario file
    """

    def __init__(self, path):
        """

        :param path: path of the scenario file to open
        :return:
        """
        self._VERSION = 1.1

        self.path = path
        self.filetable = list()
        self.spotgroups = list()
        self.computed = False  # Explain if spots have been computed
        self.masters = [list(), list(), list()]
        with open(path, 'rb') as csvfile:
            lf_reader = csv.reader(csvfile, delimiter=settings.get("scenario", "delimiter"))
            for row in lf_reader:
                self.filetable.append(row)

        for i in xrange(len(self.filetable[0]) - 1):  # Read settings values
            settings["scenario"][self.filetable[0][i + 1]] = self.filetable[1][i + 1]
        self.filetable = self.filetable[2:]  # Removing settings values
        if self._VERSION != float(settings.get("scenario", "version")):
            log.warning("Version of the scenario file unknown")

        self.comments = self.filetable[0]
        self.duration = self.filetable[1][1:]
        self.time = self.filetable[2]
        self.master_dmx = self.filetable[3][2:]
        self.master_sound = self.filetable[4][2:]
        self.master_mod = self.filetable[5][2:]
        self.filetable = self.filetable[6:]
        log.raw("Scenario settings : {0}".format(settings["scenario"]))

        settings["scenario"]["start_spotdata"] = int(settings.get("scenario", "start_spotdata")) - 8  # TODO : nawak !! !?
        for i in xrange(0, int(settings["scenario"]["n_spot"]) * settings.get("scenario", "spotdata_lines"), settings.get("scenario", "spotdata_lines")):
            spotdict = {
                "color": self.filetable[settings.get("scenario", "start_spotdata") + i],
                "R": self.filetable[settings.get("scenario", "start_spotdata") + i + 1],
                "G": self.filetable[settings.get("scenario", "start_spotdata") + i + 2],
                "B": self.filetable[settings.get("scenario", "start_spotdata") + i + 3],
                "H": self.filetable[settings.get("scenario", "start_spotdata") + i + 4],
                "S": self.filetable[settings.get("scenario", "start_spotdata") + i + 5],
                "V": self.filetable[settings.get("scenario", "start_spotdata") + i + 6],
                "deltaH": self.filetable[settings.get("scenario", "start_spotdata") + i + 7],
                "deltaS": self.filetable[settings.get("scenario", "start_spotdata") + i + 8],
                "deltaV": self.filetable[settings.get("scenario", "start_spotdata") + i + 9],
                "deltaR": self.filetable[settings.get("scenario", "start_spotdata") + i + 10],
                "deltaG": self.filetable[settings.get("scenario", "start_spotdata") + i + 11],
                "deltaB": self.filetable[settings.get("scenario", "start_spotdata") + i + 12],
            }
            self.spotgroups.append(
                lightfile.LF_SpotGroup(spotdict, self.duration, float(settings.get("scenario", "framerate"))))

        log.raw("Spotgroups : {0}".format(self.spotgroups))

    def _solve_master(self, master, master_index):
        """
        This method compute values of a master chan (dmx, mod or sound)
        :param master: row of the master
        :param master_index: master index
        :return:
        """
        n_frame = 0
        current_key = None
        key_duration = 0
        delta_frame = 0
        delta_time = 0
        last_value = 0
        framerate = float(settings.get("scenario", "framerate"))

        for i in xrange(len(master)):
            key_duration += float(self.duration[i + 1])
            if master[i] == "":  # Empty cell, just put 1
                # log.raw("master duration : {0}, calc : {1}".format(key_duration, key_duration - delta_time))
                delta_frame = lightfile.RowKey("direct:1", key_duration - delta_time,
                                               vtype="master").compute_key_to_frame_row(
                    self.masters[master_index][n_frame], framerate, n_frame,
                    self.masters[master_index])
                n_frame += delta_frame
                delta_time = (delta_frame / framerate) - key_duration
                key_duration = 0
                continue
            elif master[i] == "=":  # Wait for the order cell to get modulation
                continue
            else:
                delta_frame = lightfile.RowKey(master[i], key_duration - delta_time,
                                               vtype="master").compute_key_to_frame_row(
                    self.masters[master_index][n_frame], framerate, n_frame,
                    self.masters[master_index])
                n_frame += delta_frame
                delta_time = (delta_frame / framerate) - key_duration
                log.raw("key duration : 0{key_dur}, delta frame : {df}, delta time : {dt}".format(df=delta_frame,
                                                                                                  dt=delta_time,
                                                                                                  key_dur=key_duration))
                key_duration = 0
                continue
        log.debug(
            "master_{index}::: n_frame computed : {n_frame}, n_frame prepared : {self_frame}".format(index=master_index,
                                                                                                     n_frame=n_frame,
                                                                                                     self_frame=len(
                                                                                                         self.masters[
                                                                                                             master_index])))

    def solve_masters(self):
        """
        This method solve all masters
        :return:
        """
        self.masters = [list(), list(), list()]
        for master in range(len(self.masters)):
            for i in xrange(int(math.ceil(settings.get("scenario", "framerate") * float(
                    sum(map(float, self.duration[1:]))))) + 1):  # Generate framerate * duration frames
                self.masters[master].append(1)
        self._solve_master(self.master_dmx, 0)
        self._solve_master(self.master_mod, 1)

    def compute_all_spotgroups(self):
        """
        This method compute all spots to set them ready to export
        :return:
        """
        for spotgroup in self.spotgroups:
            spotgroup.compute_dmx()
        self.computed = True

    def write_lightfile(self):
        """
        This method write the lightfile on the disk
        :return:
        """
        if not self.computed:
            log.error("Scenario file not already computed : error")
            return
        parameters = {
            "version": str(self._VERSION),
            "framerate": str(int(settings.get("scenario", "framerate"))),
            "n_spot": str(int(settings.get("scenario", "n_spot"))),
            "dmxaddr": "/".join(["spot{0}:{1}".format(i+1, settings.get("scenario", "dmx_spot_{0}".format(i+1))) for i in
                                 range(int(settings.get("scenario", "n_spot"))) if
                                 "dmx_spot_{0}".format(i+1) in settings.get("scenario").keys()])
        }
        self.solve_masters()
        with open(self.path + ".lf", 'wb') as csvfile:
            lfwriter = csv.writer(csvfile, delimiter=settings.get("scenario", "delimiter"))
            lfwriter.writerow(["param_nom", ] + parameters.keys())
            lfwriter.writerow(["param_val", ] + parameters.values())
            lfwriter.writerow(["channel", "global dmx", "global mod"] + ["spot_" + str(i + 1) for i in range(
                int(settings.get("scenario", "n_spot")))])
            for i in range(len(self.masters[0])):
                row = list()
                row.append("")
                row.append(self.masters[0][i])
                row.append(self.masters[1][i])
                for j in range(int(settings.get("scenario", "n_spot"))):
                    row += list(self.spotgroups[j].frames[i].hsv)
                lfwriter.writerow(row)
