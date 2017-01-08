from txosc import dispatch
from txosc import async
from twisted.internet import reactor
import logging


def default_handler(message, address):
    logging.info("default_handler")
    logging.info("Got %s from %s" % (message, address))


class UDPReceiverApplication(object):
    def __init__(self, port):
        self.port = port
        self.receiver = dispatch.Receiver()
        self._server_port = reactor.listenUDP(self.port, async.DatagramServerProtocol(self.receiver))
        logging.info("Listening on osc.udp://localhost:%s" % self.port)
        self.receiver.addCallback("/", default_handler)
        self.receiver.addCallback("/dmxfade", self.dmx_fade_handler)
        self.receiver.addCallback("/dmx", self.dmx_handler)
        self.receiver.fallback = self.fallback

    @staticmethod
    def dmx_fade_handler(message, address):
        logging.info("dmx_fade_handler")
        logging.info("Got %s from %s" % (message, address))

    @staticmethod
    def dmx_handler(message, address):
        logging.info("dmx_handler")
        logging.info("Got %s from %s" % (message, address))

    @staticmethod
    def fallback(message, address):
        logging.info("Fallback :")
        logging.info("Got %s from %s" % (message, address))
