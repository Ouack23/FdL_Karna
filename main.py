import logging
from twisted.internet import reactor
from OSC import UDPReceiverApplication
from game_manager import GameManager
from array import array

UNIVERSE = 0
UPDATE = 5
DURATION = 1
DURATION_FADE = 10
CHANNELS = 4
OSC_PORT = 5000

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(threadName)s [%(threadName)s] %(levelname)s : %(message)s', level=logging.DEBUG)


_OSC = UDPReceiverApplication(OSC_PORT)
_GameManager = GameManager()
_GameManager.change_game("Simon", "RPI")
_GameManager.run_game()

reactor.run()
# GPIO.cleanup()