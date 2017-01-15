import logging, DMX, random, functions, time, pins
from array import array
from game import Game


class Simon(Game):
    def __init__(self, mode="PC"):
        Game.__init__(self, "Simon")
        self.mode = mode
        self.universe = 0
        self.duration = 1
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
        self.pins = pins.Pins()
        logging.debug("Successfully instantiated SIMON game ! :)")

    def run(self):
        if self.mode == "PC":
            logging.info("Running Simon game")

            self.seq = [self.dmx_colors.values()[random.randrange(0, 3)]]

            while not self.fail:
                for i in range(len(self.seq)):
                    self._DMX.send_dmx_and_black(self.seq[i])

                self.input_seq = raw_input("Type color sequence and press enter : ").lower()[:len(self.seq)]

                for j in range(len(self.input_seq)):
                    if self.input_seq[i] != functions.search_key_with_value(self.seq[i], self.dmx_colors):
                        self.fail = True

                if not self.fail:
                    self.seq.append(self.dmx_colors.values()[random.randrange(0, 3)])

            logging.info("That wasn't the right sequence, I am restarting the game !")
            self.stop()

        elif self.mode == "RPI":
            logging.info("Running Simon game")

            self.seq = [self.pins.pins.values()[random.randrange(0, 3)]]

            while not self.fail:
                for i in range(len(self.seq)):
                    self.pins.set_color(self.seq[i])
                    time.sleep(1)
                for i in range(len(self.seq)):
                    while self.pins.event == "wait":
                        self.pins.get_first_color_event(self.seq[i])

                    if self.pins.event == "wrong":
                        self.fail = True
                        break

                if not self.fail:
                    self.seq.append(self.pins.pins.values()[random.randrange(0, 3)])

            logging.info("That wasn't the right sequence, I am restarting the game !")
            self.stop()
        else:
            logging.info("Unknown mode : " + str(self.mode))

    def stop(self):
        self.reset()
        time.sleep(5)
        self.run()

    def reset(self):
        self.seq = []
        self.fail = False
        self.input_seq = ""
