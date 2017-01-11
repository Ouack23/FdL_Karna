import logging
from game import Game


class Simon(Game):
    def __init__(self):
        Game.__init__(self, "Simon")
        logging.debug("Successfully instantiated SIMON game ! :)")

    def run(self):
        logging.info("Running Simon game")

