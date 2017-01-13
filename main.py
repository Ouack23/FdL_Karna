import logging, pins, time
from DMX import DMX
from twisted.internet import reactor
from OSC import UDPReceiverApplication
from game_manager import GameManager
from array import array
import RPi.GPIO as GPIO

UNIVERSE = 0
UPDATE = 5
DURATION = 1
DURATION_FADE = 10
CHANNELS = 4
OSC_PORT = 5000

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(threadName)s [%(threadName)s] %(levelname)s : %(message)s', level=logging.DEBUG)

pins.gpio_setup(logging.getLevelName(logger.getEffectiveLevel()))
colors = pins.get_colors()

for i in 2*range(len(colors)):
    pins.set_color(colors[i])
    time.sleep(1)

pins.wait_for_color("blue")

# _OSC = UDPReceiverApplication(OSC_PORT)
#
# _DMX = DMX(UNIVERSE, DURATION, CHANNELS)
# _GameManager = GameManager()
# _GameManager.change_game("Simon")
# _GameManager.run_game()
# _DMX.send_dmx(array('B', [255, 0, 0, 0]))
# _DMX.send_dmx(array('B', [0, 255, 0, 0]))
# _DMX.send_dmx(array('B', [0, 0, 255, 0]))
# _DMX.send_dmx(array('B', [0, 0, 0, 255]))
#
# _DMX.set_duration(DURATION_FADE)
# _DMX.send_fade_dmx(array('B', [255, 0, 0, 0]), array('B', [0, 0, 0, 0]))

#reactor.run()
#GPIO.cleanup()
