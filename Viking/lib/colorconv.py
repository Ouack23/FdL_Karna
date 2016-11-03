# -*- coding: utf-8 -*-
#
# Color conversion module
#

import cmath
import numpy as np
import matplotlib.colors
#import cv2

def value_compressor(value, max, min=0):
    """
    This function return the value if it's in [min,max] otherwise, min if value < min or max if value > max
    :param value: value to compress
    :param max: maximum value
    :param min: minimum value
    :return: compressed value
    """
    if value > max:
        return max
    elif value < min:
        return min
    else:
        return value

def rgb_compressor(value):
    """
    Return value or 0 if value < 0 and 255 if value > 255
    :param value: Value to compress
    :return: compressed value
    """
    return value_compressor(value, 255, 0)

def hsv_compressor(value):
    """
    Return value or 0 if value < 0 and 1 if value > 1
    :param value: Value to compress
    :return: compressed value
    """
    return value_compressor(value, 1, 0)

def hue_compressor(value):
    """
    This function return the hue compressed on a circle
    :param value: hue in 0...1 or over
    :return:
    """
    if value <= 1 and value >= 0:
        return value
    elif value > 1:
        while value > 1:
            value -= 1
    else:
        while value < 0:
            value += 0
    return value

def conv_hsv_to_rgb(hsv):
    """
    This function take a HSV numpy array and convert it to a DMX ready RGB array
    :param hsv: numpy array of float values in range of 0..1
    :return: RGB numpy array of uint8 values in range 0..255
    """
    return matplotlib.colors.hsv_to_rgb(hsv) * 255

def conv_rgb_to_hsv(rgb):
    """
    This function take a RGB numpy array and convert it to a HSV (0..1) (3*1) numpy array
    :param rgb: (3*1) numpy array of int (or float) value between 0...255
    :type rgb: np.uint8
    :return: numpy array (3*1) of float values in range of 0..1
    """
    return matplotlib.colors.rgb_to_hsv(rgb / 255)

# def conv_hsv_to_rgb(hsv):
#     """
#     This function take a HSV numpy array (0..1) and convert it to a RGB (0..255) (3*1) numpy array
#     :param hsv: numpy array (3*1) of float values in range of 0..1
#     :return: (3*1) numpy array of int (or float) value between 0...255
#     """
#     return matplotlib.colors.hsv_to_rgb(hsv)

def compressor_zero_one(matrice):
    """
    Return the hsv numppy array between 0 and 1
    :param matrice:
    :return:
    """
    return np.minimum(np.maximum(matrice, 0), 1)

def linear_to_hsv(hsv, a, dt):
    """
    Apply an homotethie ret = a*dt*hsv
    :param hsv: numpy array of float values in range of 0..1
    :param a: coefficient
    :param dt: delta time
    :return:
    """
    return hsv*a*dt

def linear_to_value(value, a, dt):
    """
    Apply an homotethie ret = a*dt*value
    :param value: value
    :param a: coefficient
    :param dt: delta time
    :return:
    """
    return value*a*dt

def cos_to_hsv(hsv, a, freq, dt, phi=0):
    """
    Apply a cosine : ret = hsv * a * cos((freq*dt+phi)*2*pi)
    :param hsv:
    :param a:
    :param freq:
    :param dt:
    :return:
    """
    return hsv*a*cmath.cos(2*cmath.pi*(freq*dt+phi))

cos_to_rgb = cos_to_hsv

def cos_to_value(value, a, freq, phi, dt):
    """
    Apply a cosine : ret = value * a *cos((freq*dt+phi)*2*pi)
    :param value:
    :param a:
    :param freq:
    :param dt:
    :return:
    """
    return value*a*cmath.cos(2*cmath.pi*(freq*dt+phi)).real

def direct_to_hsv(hsv, direct_hsv, dt):
    """
    Return the given hsv
    :param hsv: hsv base value
    :param direct_hsv: hsv return value
    :param dt:
    :return:
    """
    return direct_hsv

direct_to_rgb = direct_to_hsv       # Same thing..

def direct_to_value(value, direct_value, dt):
    """
    Return the given value
    :param value: value
    :param direct_value: return value
    :param dt:
    :return:
    """
    return direct_value

def exp_to_hsv(hsv, a, dt):
    """
    Applay exponential : ret = hsv * exp(at)
    :param hsv:
    :param a:
    :param dt:
    :return:
    """
    return hsv * np.exp(a*dt)

exp_to_rgb = exp_to_hsv

def exp_to_value(value, a, dt):
    """
    Applay exponential : ret = hsv * exp(at)
    :param value:
    :param a:
    :param dt:
    :return:
    """
    return value * cmath.exp(a*dt)

def linear_paramas_from_goal(start, goal, dt):
    """
    This function return paramaters for the linear function in order to obtain the correct color after a given time
    :param start:
    :param goal:
    :param dt:
    :return:
    """
    return (goal - start)/dt

def exp_params_from_goal_hsv(start, goal, dt):
    """
    This function return parameters for the exp function in order to obtain the corect color after a given time
    :param start:
    :param goal:
    :param dt:
    :return:
    """
    return np.log(goal-start)/dt

exp_params_from_goal_rgb = exp_params_from_goal_hsv

def exp_params_from_goal_value(start, goal, dt):
    """
    This function return parameters for the exp function in order to obtain the corect color after a given time
    :param start:
    :param goal:
    :param dt:
    :return:
    """
    return cmath.log(goal-start)/dt

