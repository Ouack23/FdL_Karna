from DMX import DMX
from twisted.internet import reactor
from OSC import UDPReceiverApplication
from array import array
import logging

UNIVERSE = 0
UPDATE = 5
DURATION = 1
DURATION_FADE = 10
CHANNELS = 4
OSC_PORT = 5000

logging.basicConfig(format='%(asctime)s %(threadName)s [%(threadName)s] %(levelname)s : %(message)s', level=logging.INFO)
_OSC = UDPReceiverApplication(OSC_PORT)

_DMX = DMX(UNIVERSE, DURATION, CHANNELS)
_DMX.send_dmx(array('B', [255, 0, 0, 0]))
_DMX.send_dmx(array('B', [0, 255, 0, 0]))
_DMX.send_dmx(array('B', [0, 0, 255, 0]))
_DMX.send_dmx(array('B', [0, 0, 255, 255]))

_DMX.set_duration(DURATION_FADE)
_DMX.send_fade_dmx(array('B', [255, 0, 0, 0]), array('B', [0, 0, 0, 0]))

reactor.run()
