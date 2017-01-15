import logging, DMX, random, functions, time
from array import array
from game import Game


class Simon(Game):
    def __init__(self):
        Game.__init__(self, "Simon")
        self.mode = "PC"
        self.universe = 0
        self.duration = 1
        self.channels = 4
        self._DMX = DMX.DMX(self.universe, self.duration, self.channels)
        self.seq = []
        self.fail = False
        self.input_seq = ""
        self.color1 = array('B', [255, 0, 0, 0])
        self.color2 = array('B', [0, 255, 0, 0])
        self.color3 = array('B', [0, 0, 255, 0])
        self.color4 = array('B', [255, 255, 0, 0])
        self.colors = dict({"r": self.color1, "g": self.color2, "b": self.color3, "y": self.color4})
        logging.debug("Successfully instantiated SIMON game ! :)")

    def run(self):
        logging.info("Running Simon game")

        self.seq = [self.colors.values()[random.randrange(0, 3)]]

        while not self.fail:
            for i in range(len(self.seq)):
                self._DMX.send_dmx_and_black(self.seq[i])

            self.input_seq = raw_input("Type color sequence and press enter : ").lower()[:len(self.seq)]

            for j in range(len(self.input_seq)):
                if self.input_seq[i] != functions.search_key_with_value(self.seq[i], self.colors):
                    self.fail = True

            if not self.fail:
                self.seq.append(self.colors.values()[random.randrange(0, 3)])

        logging.info("That wasn't the right sequence, I am restarting the game !")
        self.stop()

    def stop(self):
        self.reset()
        time.sleep(5)
        self.run()

    def reset(self):
        self.seq = []
        self.fail = False
        self.input_seq = ""
