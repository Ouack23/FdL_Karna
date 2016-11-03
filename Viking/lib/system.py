# -*- coding: utf-8 -*-
#
# This file provide function and tools about the system
#

import sys

from vthread import THREAD_REGISTER
from settings import settings
from logger import init_log
import os
import master
log = init_log("sys")


def exit_on_error(error_code=1):
    """
    This function exit the programme on an error if the setting is set for
    :param error_code: Error code to return
    :return:
    """
    if settings.get("sys", "exit_on_error"):
        log.error("Aborting on error because sys.error_on_exit is set ..")
        cleanup()
        sys.exit(error_code)


def error_can_exit(logger, msg, error_code=1):
    """
    This function show up an error and exit if settings is set for this
    :return:
    """
    logger.error(msg)
    exit_on_error(error_code)


def cleanup():
    """
    This function clean all it's possible before an exiting
    :return:
    """
    for th in THREAD_REGISTER.values():
        th.exit()
        th.join(timeout=3)


def poweroff(*args, **kwargs):
    """
    This function shutdown the raspberry pi
    :return:
    """
    try:
        master.main_exit()
    except Exception:
        log.error("main_exit error")
    with open('/tmp/reboot', 'w+') as f:
        log.info("Poweroff ...")


def reboot(*args, **kwargs):
    """
    This function shutdown the raspberry pi
    :return:
    """
    try:
        master.main_exit()
    except Exception:
        log.error("main_exit error")
    with open('/tmp/reboot', 'w+') as f:
        f.write("REBOOT")
        log.info("Reboot ...")
