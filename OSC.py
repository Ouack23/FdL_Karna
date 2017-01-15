from txosc import dispatch, async
from twisted.internet import reactor, error
import logging, sys, os, time
from subprocess import check_output


def default_handler(message, address):
    logging.info("default_handler")
    logging.info("Got %s from %s" % (message, address))


class UDPReceiverApplication(object):
    def __init__(self, port):
        self.port = port
        self.receiver = dispatch.Receiver()
        try:
            self._server_port = reactor.listenUDP(self.port, async.DatagramServerProtocol(self.receiver))
        except error.CannotListenError:
            logging.error("Cannot listen port " + str(port) + ", quit already existing python instances !")
            pid_list = map(int, check_output(["pidof", "python2.7"]).split())

            logging.debug("PID python2.7 : " + str(pid_list))
            my_pid = os.getpid()
            logging.debug("My PID : " + str(my_pid))

            for i in range(len(pid_list)):
                if pid_list[i] != my_pid:
                    os.system("kill " + str(pid_list[i]))
                    logging.debug("Killing " + str(pid_list[i]))

            time.sleep(1)
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
