import logging, DMX, random, time, sys
from collections import OrderedDict
from array import array
from game import Game


def get_mode_list():
    return ["RPI", "PC"]


class Simon(Game):
    def __init__(self, mode="PC"):
        Game.__init__(self, "Simon")

        if mode in get_mode_list():
            self.mode = mode
        else:
            logging.error("This mode (" + str(mode) + ") isn't supported")
            sys.exit(0)

        self.mode = mode

        self.universe = 0
        self.duration = 0.5
        self.channels = 4
        self._DMX = DMX.DMX(self.universe, self.duration, self.channels)

        self.seq = []
        self.fail = False
        self.input_seq = ""

        self.dmx_color1 = array('B', [255, 0, 0, 0])
        self.dmx_color2 = array('B', [0, 255, 0, 0])
        self.dmx_color3 = array('B', [0, 0, 255, 0])
        self.dmx_color4 = array('B', [255, 255, 0, 0])
        self.dmx_colors = dict(r=self.dmx_color1, g=self.dmx_color2, b=self.dmx_color3, y=self.dmx_color4)

        if self.mode == "RPI":
            gpio_dict = dict(r=22, g=27, b=4, y=17)
            self.pins = None
            self.build_pins(gpio_dict)

        logging.debug("Successfully instantiated SIMON game ! :)")

    def run(self):
        if self.mode == "PC":
            logging.info("Running Simon game")

        self.seq.append(self.dmx_colors.keys()[random.randrange(0, self.channels - 1)])

        while not self.fail:
            for i in range(len(self.seq)):
                if self.mode == "RPI":
                    self.pins.set_color_and_black(self.seq[i], self.duration)
                self._DMX.send_dmx_and_black(self.dmx_colors[self.seq[i]])

            if self.mode == "PC":
                self.input_seq = raw_input("Type color sequence and press enter : ").lower()[:len(self.seq)]

                for j in range(len(self.input_seq)):
                    if self.input_seq[i] != self.seq[i]:
                        self.fail = True

            elif self.mode == "RPI":
                for i in range(len(self.seq)):
                    go_next = False
                    while not self.fail and not go_next:
                        for j in range(self.channels):
                            if self.pins.is_pressed(self.pins.get_keys()[j]):
                                if self.pins.get_keys()[j] == self.seq[i]:
                                    logging.info("Good input !!" + str(self.pins.get_values()[j]))
                                    go_next = True
                                    while self.pins.is_pressed(self.pins.get_keys()[j]):
                                        pass
                                    break
                                else:
                                    logging.info("Bad input !!" + str(self.pins.get_values()[j]))
                                    self.fail = True
                                    break
                    if self.fail:
                        break

            if not self.fail:
                self.seq.append(self.dmx_colors.keys()[random.randrange(0, self.channels - 1)])
                logging.debug("Good sequence, appending a new color : " + str(self.seq))

        logging.info("That wasn't the right sequence, I am restarting the game !")
        self.stop()

    def build_pins(self, gpio_dict):
        tmp = OrderedDict()
        import pins

        if len(gpio_dict) != len(self.dmx_colors):
            logging.error("GPIO array and DMX colors don't have the same size !")
            sys.exit(0)

        for i in gpio_dict.keys():
            if not tmp.has_key(i):
                tmp[i] = gpio_dict.get(i)

        self.pins = pins.Pins(tmp)

    def stop(self):
        self.reset()
        time.sleep(5)
        self.run()

    def reset(self):
        self.seq = []
        self.fail = False
        self.input_seq = ""
        tmp = self.duration
	self.duration = 0.4
        for i in range(0,3):
            self._DMX.send_dmx_and_black(self.dmx_colors["r"])
        self.duration = tmp
