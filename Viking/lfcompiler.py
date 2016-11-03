# -*- coding: utf-8 -*-
#

import lib.settings
lib.settings.init()

import lib.scenario

def create_lightfile():
    sfile = lib.scenario.ScenarioFile("kfet.csv")
    sfile.compute_all_spotgroups()
    sfile.write_lightfile()

create_lightfile()