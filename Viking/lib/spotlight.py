# -*- coding: utf-8 -*-
#
# This file describe a spotlight
#
#

import lib.mod
import lib.colorconv
import numpy as np


class SpotGroup(object):
    """
    A spot group is a group of DMX projector with the same DMX address
    """

    def __init__(self, group, dmx_file, dmx_out, dmx_addr, coef_matrice):
        """

        :param group: Projector group in files
        :param dmx_file: Pointer to the dmx file with HSV values
        :param dmx_out: (255*1) uint8 matrice with is the dmx output matrice
        :param dmx_addr: Address DMX of the SpotGroup in 0 .. 255
        :param coef_matrice: (9*15) Current coef_matrice for modulation
        :return:
        """
        self.group = group
        self._gourp_addr = (self.group - 1) * 3
        self._group_addr_end = self._gourp_addr + 3
        self.dmx_file = dmx_file
        self.dmx_out = dmx_out
        self.dmx_addr = dmx_addr
        self._dmx_add_end = dmx_addr + 3
        self.coef_matrice = coef_matrice
        self.delta_hsv = np.float32((0, 0, 0))

    def _read_frame(self, frame):
        """
        This private methode return the unmodulate HSV (3*1) matrice
        :param frame: frame number
        :return: (3*1) HSV matrice unmodulated
        """
        return self.dmx_file[frame][self._gourp_addr:self._group_addr_end]

    def compute_delta(self, capteur):
        """
        This method compute the delta HSV for a given capteur matrice
        :param capteur: (9*15) capteur matrice
        :return: (3*1) delta HSV matrice
        """
        self.delta_hsv = lib.mod.compute_modulation(capteur, self.coef_matrice)

    def compute_frame(self, frame):
        """
        This method compute the RGB value of a given frame
        :param frame: Frame number
        :return: (3*1)
        """
        self.dmx_out[self.dmx_addr:self._dmx_add_end] = lib.colorconv.conv_hsv_to_rgb(
            self._read_frame(frame) + self.delta_hsv
        )
