from DMX import DMX
from DMX_fade import DMXFade
from twisted.internet import threads, reactor, defer
from OSC import UDPReceiverApplication
from array import array
import logging
import time

UNIVERSE = 0
UPDATE = 5
DURATION = 1000
CHANNELS = 4
OSC_PORT = 5000

logging.basicConfig(format='%(asctime)s %(threadName)s [%(threadName)s] %(levelname)s : %(message)s', level=logging.DEBUG)
UDPReceiverApplication(OSC_PORT)

_DMX = DMX(UNIVERSE, DURATION, CHANNELS)
_DMX.run_dmx()

_DMX.send_dmx(array('B', [255, 0, 0, 0]))
_DMX.run_dmx()
_DMX.send_dmx(array('B', [0, 255, 0, 0]))
_DMX.run_dmx()
_DMX.send_dmx(array('B', [0, 0, 255, 0]))
_DMX.run_dmx()
_DMX.send_dmx(array('B', [0, 0, 255, 255]))
_DMX.run_dmx()

_DMX_fade = DMXFade(UNIVERSE, DURATION, CHANNELS)
_DMX_fade.set_duration(10000)
_DMX_fade.fade_dmx(array('B', [255, 0, 0, 0]), array('B', [0, 0, 0, 0]), UPDATE)
