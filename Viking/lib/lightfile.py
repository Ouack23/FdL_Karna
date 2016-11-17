# -*- coding: utf-8 -*-
#
# This file provide function to create a binary light file from a JSON light scenario
#


import colorconv
import numpy as np
import math
import mathmod
import csv
import dmx

from lib.settings import settings

import logger
log = logger.init_log("lightfile")

CONVERTER_VERSION = 0.1


# def log(msg, err=False):
#     if err:
#         print("/!!\ " + msg)
#     else:
#         print(msg)




def get_color_from_txt(txt):
    """
    Return the colorspace and the color value from a txt as rgb(145,234,10) => rgb,(145,234,10)
    :param txt: txt as rgb(145,234,10) or hsv(0.1,0.4,0.5)
    :return: tuple : (colorspace,(x,y,z))
    """
    return txt[0:3], txt[4:-1].split(",")


def get_rgb_from_txt(txt):
    """
    This function return a numpy array RGB from txt
    :param txt: txt as rgb(145,234,10) or hsv(0.1,0.4,0.5)
    :return:
    """
    txt = get_color_from_txt(txt)
    if txt[0] == "rgb":
        return np.float32(txt[1])
    else:
        return colorconv.conv_hsv_to_rgb(txt[1])


def compute_previous(key, frame, *args):
    """

    :param key:
    :param frame:
    :param a:
    :param freq:
    :param phi:
    :return:
    """
    value = 1
    if key.vtype in (0,1,2):
        value = frame.rgb[key.vtype]
    elif key.vtype in (3,4,5):
        value = frame.hsv[int(key.vtype)-3]
    elif key.vtype == "color":
        value = frame.rgb
    else:
        log.warning("compute_previous only for color,R,G,B,H,S,V params")
    return [value, ] + list(args)





class RowKey(object):
    """
    This class represent a key (color,r,g,b,h,s,v)
    """

    def __init__(self, txt, duration, vtype="color", stop=False):
        """

        :param txt: txt of the key
        :param duration: duration of the key, if there is empty key after duration will be the sum of theme
        :param vtype: value type, color or 0,1,2,3.. (0=R,1=G...)
        :param stop: explain if it's a stop key
        :return:
        """
        self.txt = txt
        self.vtype = vtype
        self.duration = duration
        self.stop = stop

    def compute_key_to_frame_row(self, start_value, framerate, start_frame, frames):
        """
        This function return a list of values
        :param start_value: value just before the current key
        :param framerate: number of frame per second
        :param start_frame: frame number of the first frame of the key
        :param frames: frames to write in
        :return: number of frame computed
        """
        txt = self.txt.split(":")
        fnct = None
        args = []
        kwargs = {}
        set = '+'
        goal_color = None
        compute_args_fnct = None
        compute_args = None
        if self.vtype not in ("color","master") and txt[0] == "set":  # Parameter are not relative (delta) but fixed (set)
            set = '='
            txt = txt[1:]  # Removing 'set' from txt
        if self.vtype == "color" and txt[0] != "cos":
            goal_color = np.float32(get_rgb_from_txt(txt[1]))
        if txt[0] == "direct":
            if self.vtype == "color":
                fnct = colorconv.direct_to_rgb
                args = [start_value, goal_color]
            else:
                fnct = colorconv.direct_to_value
                args = [start_value, float(txt[1])]
        elif txt[0] == "exp":
            if self.vtype == "color":
                fnct = mathmod.change_exp_to_rgb
                goal_color_hsv = colorconv.conv_rgb_to_hsv(goal_color)
                start_value_hsv = colorconv.conv_rgb_to_hsv(start_value)
                a = np.float32((0, 0, 0))
                sign = np.int8((1, 1, 1))
                for i in range(3):
                    sign[i], a[i] = mathmod.coef_exp(start_value[i], goal_color[i], self.duration)
                args = [start_value, a, sign]
            else:
                fnct = mathmod.change_exp
                args = list(mathmod.coef_exp(start_value, float(txt[1]), self.duration))
            log.raw("exp coef {0}".format(args))
        elif txt[0] == "mexp":
            if self.vtype == "color":
                fnct = mathmod.change_mexp_to_rgb
                goal_color_hsv = colorconv.conv_rgb_to_hsv(goal_color)
                start_value_hsv = colorconv.conv_rgb_to_hsv(start_value)
                a = np.float32((0, 0, 0))
                sign = np.int8((1, 1, 1))
                for i in range(3):
                    sign[i], a[i] = mathmod.coef_mexp(start_value[i], goal_color[i], self.duration)
                #compute_args_fnct = compute_previous
                args = [np.maximum(start_value,goal_color), -a, -sign]
            else:
                fnct = mathmod.change_mexp
                compute_args_fnct = compute_previous
                compute_args = list(mathmod.coef_mexp(start_value, float(txt[1]), self.duration))
            log.raw("exp coef {0}".format(args))
        elif txt[0] == "cos":
            if self.vtype == "color":
                log.error("depreciate to set a cos to a color")
            else:
                fnct = colorconv.cos_to_value
                a,freq,phi = txt[1].split("/")
                value = 1
                args = [value, float(a), float(freq), float(phi)]
        elif txt[0] == "mcos":
            if self.vtype == "color":
                log.error("depreciate to set a cos to a color")
            else:
                fnct = colorconv.cos_to_value
                a,freq,phi = txt[1].split("/")
                compute_args_fnct = compute_previous
                compute_args = [float(a), float(freq), float(phi)]

        i = 0
        max_i = int(math.ceil(start_frame + self.duration * framerate))
        log.raw("{txt} , start frame : {start_frame} max i compute : {max_i}".format(txt=txt, start_frame=start_frame,
                                                                                   max_i=max_i))
        for i in xrange(start_frame, max_i, 1):
            if compute_args_fnct is not None:        # Calculate args on the fly
                args = compute_args_fnct(self, frames[i-1], *compute_args)
            if self.vtype == "color":
                try:
                    frames[i].set_color(colorspace='rgb', color=fnct(*args, dt=float(i - start_frame) / framerate))
                    # print("{i}: {color}, {txt}".format(i=i, color=frames[i].rgb, txt=txt))
                except IndexError:
                    log.error("I : {1} MAX I : {0}".format(max_i, i))
            elif self.vtype == "master":
                frames[i] = fnct(*args, dt=float(i - start_frame) / framerate)
            else:
                frames[i].set_value(self.vtype, value=fnct(*args, dt=float(i - start_frame) / framerate), mode=set)
        return i - start_frame + 1


class LF_SpotGroup(object):
    """
    This class represent a SpotGroup in a lightfile
    """

    def __init__(self, lf_part, lf_duration, framerate=25):
        """

        :param lf_part: dict of LightFile partition for the spotgroup
        :param lf_duration: LightFile duration
        :param framerate: Framerate of the lightfile
        :return:
        """
        self.lf_part = lf_part
        self.lf_duration = lf_duration
        self.framerate = float(framerate)
        self.frames = list()
        self.dmx_ready = False      # Explain if the dmx have been already computed
        for i in xrange(int(math.ceil(framerate * float(
                sum(map(float, self.lf_duration))))) + 1):  # Generate framerate * duration frames
            self.frames.append(Frame())

    def solve_color(self, lf_color_row):
        """
        This method solve the color value on each frame with the
        :param lf_color_row: list of keys with color order
        :return:
        """
        log.raw("color row : {0}".format(lf_color_row))
        lf_color_row = lf_color_row[1:]  # Remove cell with the name as 'color1'
        n_frame = 0
        current_key = None
        key_duration = 0
        delta_frame = 0
        delta_time = 0

        self.frames[n_frame].set_color(*get_color_from_txt(lf_color_row[0].split(":")[1]))  # Set first color
        lf_color_row = lf_color_row[1:]
        n_frame += 0
        for i in xrange(len(lf_color_row)):
            key_duration += float(self.lf_duration[i + 1])
            if lf_color_row[i] == "":  # Empty cell, next one will stay longer
                continue
            elif lf_color_row == "/":  # End modulation cell
                current_key = RowKey("direct:rgb({0},{1},{2})".format(*self.frames[n_frame-1].rgb), 0, stop=True)
                continue
            else:
                if current_key is not None and current_key.stop:
                    # Last key was a stop
                    log.error("STOP KEY NOT IMPLEMENTED FOR COLOR")
                delta_frame = RowKey(lf_color_row[i], key_duration - delta_time).compute_key_to_frame_row(
                    self.frames[n_frame-1].rgb, self.framerate, n_frame, self.frames)
                n_frame += delta_frame
                delta_time = (delta_frame / self.framerate) - key_duration
                log.raw("key duration : 0{key_dur}, delta frame : {df}, delta time : {dt}".format(df=delta_frame,
                                                                                                dt=delta_time,
                                                                                                key_dur=key_duration))
                key_duration = 0
                continue
        log.debug("color::: n_frame computed : {n_frame}, n_frame prepared : {self_frame}".format(n_frame=n_frame,
                                                                                              self_frame=len(
                                                                                                  self.frames)))

    def _solve_param(self, lf_param_row, index):
        """
        This method compute values of a given parameter
        :param lf_param_row: lf_row of the parameter
        :param index: index of the parameter : 0=R,1=G,2=B,3=H..
        :return:
        """
        lf_param_row = lf_param_row[2:]  # Remove the cell with 'h1' or 'r2' .. and the first one
        n_frame = 0
        current_key = None
        key_duration = 0
        delta_frame = 0
        delta_time = 0
        last_value = 0

        for i in xrange(len(lf_param_row)):
            key_duration += float(self.lf_duration[i + 1])
            if lf_param_row[i] == "":  # Empty cell, just put 0
                delta_frame = RowKey("direct:0", key_duration - delta_time, vtype=index).compute_key_to_frame_row(
                    self.frames[n_frame-1].values[index][1], self.framerate, n_frame, self.frames)
                n_frame += delta_frame
                delta_time = (delta_frame / self.framerate) - key_duration
                key_duration = 0
            elif lf_param_row[i] == "=":  # Wait for the order cell to get modulation
                continue
            else:
                delta_frame = RowKey(lf_param_row[i], key_duration - delta_time, vtype=index).compute_key_to_frame_row(
                    self.frames[n_frame-1].values[index][1], self.framerate, n_frame, self.frames)
                n_frame += delta_frame
                delta_time = (delta_frame / self.framerate) - key_duration
                log.raw("key duration : 0{key_dur}, delta frame : {df}, delta time : {dt}".format(df=delta_frame,
                                                                                                dt=delta_time,
                                                                                                key_dur=key_duration))
                key_duration = 0
                continue
        log.debug("index_{index}::: n_frame computed : {n_frame}, n_frame prepared : {self_frame}".format(index=index,
                                                                                                      n_frame=n_frame,
                                                                                                      self_frame=len(
                                                                                                          self.frames)))

    def solve_parameters(self, lf_parameters_rows):
        """
        This function compute all values of parameters
        :param lf_parameters_rows: row of all parameters (R,G,B,H,S,V)
        :return:
        """
        for index in range(6):
            self._solve_param(lf_parameters_rows[index], index)

    def compute_dmx(self):
        """
        This methode compute color and all parameters of the spotgroup to set them ready to be exported
        :return:
        """
        self.solve_color(self.lf_part["color"])
        self.solve_parameters(
            (
                self.lf_part["R"],
                self.lf_part["G"],
                self.lf_part["B"],
                self.lf_part["H"],
                self.lf_part["S"],
                self.lf_part["V"]
            )
        )
        self.dmx_ready = True



class Frame(object):
    """
    This class represent a frame for a spotgroup
    """

    def __init__(self):
        self.rgb = np.float32([0, 0, 0])
        self.values = [
            ['+', 0],  # r
            ['+', 0],  # g
            ['+', 0],  # b
            ['+', 0],  # h
            ['+', 0],  # s
            ['+', 0]  # v
        ]
        self.hsv = np.float32([0,0,0])

    def set_color(self, colorspace, color):
        """
        Set base color of the frame
        :param colorspace: colorspace of the given color, rgb or hsv
        :param color: color tuple
        :return:
        """
        if colorspace == "rgb":
            self.rgb = np.float32(color)
        elif colorspace == "hsv":
            self.rgb = colorconv.conv_hsv_to_rgb(color)
        else:
            log.error("set_color need rgb or hsv colorspace, get : {0}".format(colorspace))
            return
        self.compute_frame()

    def set_value(self, index, value, mode="+"):
        """
        Set a value (R,G,B,H,S,V) with his mode set (+,=)
        :param index: index of the value, 0 for R, 1 for G , 2 for B ... etc
        :param value: value
        :param mode: + for delta, = for set
        :return:
        """
        self.values[index] = [mode, value]
        self.compute_frame()

    def compute_frame(self):
        """
        This methode compute the final HSV value of the frame
        :return:
        """
        for i in range(3):  # Add or set R,G,B with compressor (0..255)
            if self.values[i][0] == '+':
                self.rgb[i] += self.values[i][1]
            elif self.values[i][0] == "=":
                self.rgb[i] = self.values[i][1]
            self.rgb[i] = colorconv.rgb_compressor(self.rgb[i])
        self.hsv = colorconv.conv_rgb_to_hsv(self.rgb)
        for i in range(3):  # Add or set H,S,V with compressor (0..1)
            if self.values[3 + i][0] == '+':
                self.hsv[i] += self.values[3 + i][1]
            elif self.values[3 + i][0] == "=":
                self.hsv[i] = self.values[3 + i][1]
            if i > 0:
                self.hsv[i] = colorconv.hsv_compressor(self.hsv[i])
            else:       # Use a circular compressor on hue to render color on a circle
                self.hsv[i] = colorconv.hue_compressor(self.hsv[i])

    def __str__(self):
        return "{rgb} R{0}{1} G{2}{3} B{4}{5} H{6}{7} S{8}{9} V{10}{11}\n == {hsv}\n".format(
                                                                                self.values[0][0],
                                                                                self.values[0][1],
                                                                                self.values[1][0],
                                                                                self.values[1][1],
                                                                                self.values[2][0],
                                                                                self.values[2][1],
                                                                                self.values[3][0],
                                                                                self.values[3][1],
                                                                                self.values[4][0],
                                                                                self.values[4][1],
                                                                                self.values[5][0],
                                                                                self.values[5][1],
                                                                                rgb=self.rgb,
                                                                                hsv=self.hsv
                                                                                )

    def __repr__(self):
        return self.__str__()


class LightFile(object):
    """
    This class represent a lightfile charged in memory as parameters and numpy arrays
    """
    def __init__(self, path):
        """

        :param path: path to the light file (csv format)
        :return:
        """
        self._VERSION = 1.1
        self.path = path
        self.parameters = dict()
        self.master_dmx = None
        self.master_mod = None
        self.frames = None
        self.spots = list()

    def read(self):
        """
        This method read the csv file and agregate datas in
        :return:
        """
        filetable = list()
        modtable = list()
        # READ LIGHT FILE
        with open(self.path, 'rb') as csvfile:
            lf_reader = csv.reader(csvfile, delimiter=str(settings.get("scenario", 
"delimiter")))
            for row in lf_reader:
                filetable.append(row)
        for i in xrange(len(filetable[0]) - 1):  # Read settings values
            settings["lightfile"][filetable[0][i + 1]] = filetable[1][i + 1]
        filetable = filetable[3:]  # Removing settings values and channel name
        # READ MODULATION FILE
        with open(".".join(self.path.split(".")[:-1]), 'rb') as csvfile:        # read mod file (- .lf)
            lf_reader = csv.reader(csvfile, delimiter=str(settings.get("scenario",
"delimiter")))
            for row in lf_reader:
                modtable.append(row)
        for i in xrange(len(modtable[0]) - 1):  # Read settings values
            settings["scenario"][modtable[0][i + 1]] = modtable[1][i + 1]
        #modtable = modtable[int(settings.get("scenario", "start_spotdata")):]

        if self._VERSION != float(settings.get("lightfile", "version")):
            log.warning("Version of the light file unknown")
        n_spot = int(settings.get("lightfile", "n_spot"))
        self.frames = np.zeros((len(filetable), n_spot*3), dtype=np.float32)
        self.master_dmx = np.ones(len(filetable), dtype=np.float32)
        self.master_mod = np.ones(len(filetable), dtype=np.float32)
        for i in range(len(filetable)):
            self.master_dmx[i] = filetable[i][1]
            self.master_mod[i] = filetable[i][2]
            self.frames[i] = filetable[i][3:]
        log.debug("Lightfile with {0} frames".format(len(self.frames)))
        log.raw(str(self.frames))

        dmxaddr = dict()
        for addr in settings.get("lightfile", "dmxaddr").split("/"):
            addr = addr.split(":")
            dmxaddr[addr[0]] = int(addr[1])

        for i in range(int(settings.get("lightfile", "n_spot"))):
            self.spots.append(dmx.DmxGroup(i*3, self.frames, dmxaddr["spot{0}".format(i+1)], None, modtable[
                int(settings.get("scenario", "start_spotdata"))+(i+1)*int(settings.get("scenario", "spotdata_lines"))-6:
                int(settings.get("scenario", "start_spotdata"))+(i+1)*int(settings.get("scenario", "spotdata_lines"))
            ], modtable[4][1:]))


def rien():
    pass


#
#
# class SpotlightScenario:
#     """
#     This class describe what append to a spotlight during a scenario
#     """
#
#     def __init__(self, index, jlight):
#         """
#         :param index: Index of the projector to find information in jlight
#         :param jlight: JSON light file
#         """
#         self.index = index
#         self._jlight = jlight
#         self._framesize = struct.calcsize("3f")  # Frame size in bytes
#         self._framerate = jlight["framerate"]  # Frame rate
#         self._frameduration = 1 / float(self._framerate)  # Frame duration in seconds
#         self._framecursor = 0  # Current frame
#         self._keycursor = 0  # Current key cursor
#         self.frames = list()
#         #self.frames.append(None)  # First color is black /!\ maybe wrong idea for loop /!\
#         #self.frames[0] = (0, 0, 0)
#         self.find_firstcolor()
#         self._firstkey = None
#
#     def find_firstcolor(self):
#         """
#         :return:
#         """
#         for keys in self._jlight["keys"]:
#             for change in keys["changes"]:
#                 if change["spot"] == self.index:
#                     if change["value"][:3] == "rgb":
#                         next_color = list(colorsys.rgb_to_hsv(*[float(x) / 255 for x in change["value"][4:-1].split(",")]))
#                     if change["value"][:3] == "hsv":
#                         next_color = [float(x) for x in change["value"][4:-1].split(",")]  # 0.1,0.34,0.2 => (0.1,0.34,0.2)
#                     break
#         self.frames.append(next_color)
#
#     def compute_next_key(self):
#         """
#
#         :return:
#         """
#         next_key = None
#         duration = 0
#         while True:
#             next_key = self._jlight["keys"][self._keycursor]
#             self._keycursor += 1    # Keep in mind that we've just read a step
#             duration += next_key["duration"]        # Add step duration to keep sync
#             for change in next_key["changes"]:      # Now search ourself in this key
#                 if self.index in change["spot"]:    # Found
#                     next_key = change
#                     break  # Found the next key !
#             if self._keycursor >= len(self._jlight["keys"]):  # If there is no next key because of ending file
#                 #next_key = None
#                 end_file = True
#                 log("end file")
#                 break
#                 if next_key is not None:    # ???? If there isn't a change for us, continue with this duration
#                 break
#
#
#     @staticmethod
#     def linear_interpolation(t, hsv, k=(1, 1, 1)):
#         """
#         This function return hsv for a given time
#         :param t: time
#         :param hsv: current tuple H, S, V
#         :param k: linear parameter for each value
#         :return: new H, S, V
#         """
#         return hsv[0] + k[0] * t, hsv[1] + k[1] * t, hsv[2] + k[2] * t
#
#     def _compute_next_key(self):
#         """
#         This method compute frame until next key
#         """
#         next_key = None
#         end_file = False
#         duration = 0
#         while True:  # Search next key which describe a change for the spot
#             next_key = self._jlight["keys"][self._keycursor]
#             self._keycursor += 1
#             duration += next_key["duration"]
#             for change in next_key["changes"]:
#                 if self.index in change["spot"]:
#                     next_key = change
#                     break  # Found the next key !
#             if self._keycursor >= len(self._jlight["keys"]):  # If there is no next key because of ending file
#                 #next_key = None
#                 end_file = True
#                 log.log("raw","endfile")
#                 break
#             if next_key is not None:
#                 break
#
#         if next_key is None:  # If there is no other next_key (end of file)
#             # fnct = SpotlightScenario.linear_interpolation
#             # kwargs = {"k": (0, 0, 0)}
#             fnct, kwargs, duration = self._firstkey
#         else:
#             # Find next color step #
#             next_color = None
#             if change["type"] == "color":
#                 if change["value"][:3] == "rgb":
#                     next_color = list(colorsys.rgb_to_hsv(*[float(x) / 255 for x in change["value"][4:-1].split(",")]))
#                 if change["value"][:3] == "hsv":
#                     next_color = [float(x) for x in change["value"][4:-1].split(",")]  # 0.1,0.34,0.2 => (0.1,0.34,0.2)
#             elif change["type"] == "set":
#                 next_color = list(self.frames[-1][0], self.frames[-1][1], self.frames[-1][2])
#                 if "h" in change.keys():
#                     next_color[0] = float(change["h"])
#                 if "s" in change.keys():
#                     next_color[1] = float(change["s"])
#                 if "v" in change.keys():
#                     next_color[2] = float(change["v"])
#             elif change["type"] == "move":
#                 next_color = list(self.frames[-1][0], self.frames[-1][1], self.frames[-1][2])
#                 if "h" in change.keys():
#                     next_color[0] += float(change["h"])
#                 if "s" in change.keys():
#                     next_color[1] += float(change["s"])
#                 if "v" in change.keys():
#                     next_color[2] += float(change["v"])
#             else:
#                 log.error("There is no correct color defined in key {0} : {1}".format(self._keycursor, next_key))
#                 next_color = self.frames[-1]
#             next_color[0] %= 1
#             if next_color[1] > 1:
#                 next_color[1] = 1
#             elif next_color[1] < 0:
#                 next_color[1] = 0
#             if next_color[2] > 1:
#                 next_color[2] = 1
#             elif next_color[2] < 0:
#                 next_color[2] = 0
#             #############################################
#             # Find interpolation and correct parameters #
#             if change["int"] == "lin":  # Linear interpolation
#                 k = list()
#                 k.append((next_color[0] - self.frames[-1][0]) / (duration * self._framerate))
#                 k.append((next_color[1] - self.frames[-1][1]) / (duration * self._framerate))
#                 k.append((next_color[2] - self.frames[-1][2]) / (duration * self._framerate))
#                 fnct = SpotlightScenario.linear_interpolation
#                 kwargs = {"k": k}
#                 #############################################
#         # Compute frames with function and parameters #
#         if self._firstkey is None:
#         #     self._firstkey = True
#         # elif self._firstkey is True:
#             self._firstkey = (fnct, kwargs, duration)
#         start_color = self.frames[-1]
#         for t in xrange(0, int(duration * self._framerate)):
#             # t /= self._framerate
#             self.frames.append(fnct(t, start_color, **kwargs))
#         ###############################################
#         return end_file  # None if it's the end
#
#     def compute_frames(self):
#         """
#         This methode compute all frames for the current spotlight
#         """
#         end_file = False
#         while end_file is not True:
#             end_file = self.compute_next_key()
#
#
# def get_frames_amount(jlight):
#     """
#     This function return the number of frames into the scenario
#     :param jlight: JSON object of light file
#     :return:
#     """
#     n_sec = 0  # Number of seconds in the scenario
#     for i in xrange(len(jlight["keys"])):
#         # Assert duration is an integer * 1/framerate #
#         jlight["keys"][i]["duration"] = int(jlight["keys"][i]["duration"] * jlight["framerate"]) / float(
#             jlight["framerate"])
#         ####################################
#         n_sec += jlight["keys"][i]["duration"]
#     return n_sec * jlight["framerate"]  # Number of frame
#
#
# def convert_json_to_lightfile(json_path, lightfile_path):
#     """
#     This function convert a JSON lightfile to a binary lightfile
#     :param json_path: JSON file path
#     :param lightfile_path: Exported binary lightfile path
#     :return:
#     """
#
#     with open(json_path, "r") as fd:
#         jlight = json.load(fd)
#
#     with open(lightfile_path, "wrb") as binlight:
#         # HEADER #
#         binlight.write(struct.pack("I", CONVERTER_VERSION * 100))  # Binary light file version
#         binlight.write(struct.pack("H", int(len(jlight["spotlights"]))))  # Amount of spotlights
#         binlight.write(struct.pack("I", int(get_frames_amount(jlight))))  # Number of frame
#         binlight.write(struct.pack("H", int(jlight["framerate"])))  # Framerate
#         ##########
#         spotlights = list()
#         for spot in jlight["spotlights"]:
#             spot = SpotlightScenario(spot, jlight)
#             spot.compute_frames()
#             spotlights.append(spot.frames)
#         for i in xrange(len(spotlights[0])):
#             for spot in spotlights:
#                 binlight.write(struct.pack("f", spot[i][0])) # H
#                 binlight.write(struct.pack("f", spot[i][1])) # S
#                 binlight.write(struct.pack("f", spot[i][2])) # V
#
#
# def get_and_move(fmt, offset, fd):
#     """
#     This function return a value as the struct.unpack but manage offset
#     :param fmt: Format of the searched value
#     :param offset: Offset of the cursor
#     :param fd: File descriptor
#     :return: data and offset
#     """
#     return struct.unpack_from(fmt, fd, offset.move(struct.calcsize(fmt)))
#
#
# class Offset:
#     """
#     This class is just an offset descriptor
#     """
#
#     def __init__(self):
#         self._offset = 0
#
#     def move(self, value):
#         offset = self._offset
#         self._offset += value
#         return offset
#
#     @property
#     def offset(self):
#         return self._offset
#
#     @offset.setter
#     def offset(self, value):
#         self._offset = value
#
#
# def debug_lightfile(lightfile_path):
#     """
#     This function show a readable view of a binary lightfile
#     :param lightfile_path: Path to the binary light file
#     :return:
#     """
#     out = "\n"
#     offset = Offset()
#     with open(lightfile_path, "rb") as fbinlight:
#         binlight = fbinlight.read()
#     out += "VERSION {0}".format(get_and_move("I", offset, binlight)[0] / 100.0) + "\n"
#     nspots = get_and_move("H", offset, binlight)[0]
#     out += "Spotlights : {0}".format(nspots) + "\n"
#     nframes = get_and_move("I", offset, binlight)[0]
#     out += "Number of frames : {0}".format(nframes) + "\n"
#     out += "Framerate : {0} ".format(get_and_move("H", offset, binlight)[0]) + "\n"
#     for i in xrange(nframes):
#         out += "Frame n°{0}".format(i) + "\n"
#         for spot in xrange(nspots):
#             out += "[" + str(get_and_move("f", offset, binlight)[0]) + "," + str(
#                 get_and_move("f", offset, binlight)[0]) + "," + str(get_and_move("f", offset, binlight)[0]) + "]"
#         out += "\n"
#     return out
#
#
# def import_lightfile(lightfile_path):
#     """
#     This function read a light file and return headers information an datas
#     :param lightfile_path: Path to the binary light file
#     :return: header, datas
#     """
#     header = {}
#     offset = Offset()
#     with open(lightfile_path, "rb") as fbinlight:
#         binlight = fbinlight.read()
#     header["version"] = float(get_and_move("I", offset, binlight)[0] / 100.0)
#     header["spotlights"] = get_and_move("H", offset, binlight)[0]
#     header["frames"] = get_and_move("I", offset, binlight)[0]
#     header["framerate"] = get_and_move("H", offset, binlight)[0]
#     return header, binlight[offset.offset:]
#
#
#
