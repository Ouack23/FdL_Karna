# -*- coding: utf-8 -*-
#
#
# This file provide class and tools for sound manipulation
#


import pyo


class SoundFile(pyo.SndTable):
    """
    This class is the base classe for a sound file object
    """

    def __init__(self, path, chnl=None):
        """
        :param path: Sound file path
        :param chnl: Number of channel to read in, default None read all
        :return:
        """
        pyo.SndTable.__init__(self, path, chnl)



