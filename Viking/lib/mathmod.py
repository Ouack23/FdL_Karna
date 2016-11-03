# -*- coding: utf-8 -*-
#
# This file provide function to modulate values or arrays with mathemathical functions
#

import collections
import cmath
import numpy as np
import colorconv

import logger
log = logger.init_log("mathmod")

def coef_exp(start_value, end_value, dt):
    """
    This function return the a parameter solving this equation end = start + sign(end-start)*(exp(a*dt)-1) ) and sign
    :param start_value:
    :param end_value:
    :param dt:
    :return: sign,a
    """
    sign = None
    if end_value > start_value:
        sign = 1
    elif end_value < start_value:
        sign = -1
    else:
        log.warning("expontential cannot have same start and end value")
        sign = 0.00001
    return sign, cmath.log(sign * (end_value - start_value) + 1).real / dt


def coef_mexp(start_value, end_value, dt):
    """
    This function return the a parameter solvingg this equation end = start * (1+sign(start-end)*exp(a*dt)) and sign
    :param start_value:
    :param end_value:
    :param dt:
    :return: sign, a
    """
    sign = None
    if end_value > start_value:
        sign = -1
    elif end_value < start_value:
        sign = 1
    else:
        log.warning("expontential cannot have same start and end value")
        sign = 0.00001
    if start_value - end_value - sign * 1 == 0:  # Avoid math error
        if sign > 0:
            start_value *= 0.99
        else:
            end_value *= 0.99
    return sign, cmath.log(start_value - end_value - sign * 1).real / dt


def change_exp(a, sign, dt):
    """
    This function return the instant value of a color or param during a exp change
    :param a: exp parameter
    :param sign:
    :return:
    """
    exp = np.exp(dt * a)
    return sign * (exp - 1)


def change_mexp(start_value, a, sign, dt):
    """
    This function return the instant value of a color or param during a exp change
    :param a: exp parameter
    :param sign:
    :return:
    """
    exp = np.exp(dt * a)
    if isinstance(sign, collections.Iterable):
        ret = np.zeros(len(sign), dtype=np.float32)
        for i in range(len(sign)):
            if sign[i] > 0:
                ret[i] = start_value[i] * (1 - exp[i])
            elif sign[i] < 0:
                ret[i] = start_value[i] * exp[i]
        #log.raw("retour mexp : {0}, start {1}".format(ret, start_value))
        return ret
    if sign > 0:
        return start_value * (1 - exp)
    elif sign < 0:
        return start_value * exp

def change_exp_to_rgb(start_color, *args, **kwargs):
    """

    :param args:
    :param kwargs:
    :return:
    """
    return start_color + change_exp(*args, **kwargs)

def change_mexp_to_rgb(start_color, *args, **kwargs):
    """

    :param args:
    :param kwargs:
    :return:
    """
    return change_mexp(start_color, *args, **kwargs)