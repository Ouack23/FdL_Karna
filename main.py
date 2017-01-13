import logging
from twisted.internet import reactor
from OSC import OSC
from game_manager import GameManager
from subprocess import check_output

try:
    UNIVERSE = 0
    UPDATE = 5
    DURATION = 1
    DURATION_FADE = 10
    CHANNELS = 4
    OSC_PORT = 5000

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(asctime)s %(threadName)s [%(threadName)s] %(levelname)s : %(message)s', level=logging.DEBUG)

    _OSC = OSC(OSC_PORT)
    _GameManager = GameManager()

    if check_output(["uname", "-m"]).find("armv7") != -1:
        _GameManager.change_game("Simon", "RPI")
    else:
        _GameManager.change_game("Simon", "PC")

    _GameManager.run_game()

    reactor.run()

except KeyboardInterrupt:
    logging.info("Quitting because of ctrl + C")
