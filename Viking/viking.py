#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# This is the main file of the viking projet
#

import time

import lib.settings
import lib.logger
import lib.master

lib.settings.init()
settings = lib.settings.settings
log = lib.logger.init_log("main")


try:
    lib.master.main_init()
    lib.master.main_start_clock()
    if not settings.get("sys", "raspi"):
        lib.master.emulate_input()
    else:
        try:
            while not lib.master.shutdown.is_set():
                time.sleep(1)
            log.info("Shuting down..")
        except Exception as e:
            log.error("Error : {0}".format(e))
except Exception as e:
    log.error("Error on main : {0}".format(e))
finally:
    lib.master.main_exit()


