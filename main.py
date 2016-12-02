from DMX import DMX
from ola.ClientWrapper import ClientWrapper
from array import array


UNIVERSE = 0
UPDATE = 5
DURATION = 2000
CHANNELS = 4

DMX = DMX(UNIVERSE, ClientWrapper(), DURATION, CHANNELS)

DMX.SendDMX(array('B', [255, 0, 0, 0]))
DMX.Run()

DMX.SendDMX(array('B', [0, 255, 0, 0]))
DMX.Run()

DMX.SendDMX(array('B', [0, 0, 255, 0]))
DMX.Run()

DMX.set_duration(10000)
if(DMX.FadeDMX(array('B', [255, 0, 0, 0]), array('B', [0, 0, 0, 0]), UPDATE)):
    DMX.Run()