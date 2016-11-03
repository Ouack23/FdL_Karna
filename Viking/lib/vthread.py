# -*- coding: utf-8 -*-
#
# Viking thread
#
#

import threading
import Queue

from settings import settings
from logger import init_log
log = init_log("vthread")


THREAD_REGISTER_LOCK = threading.Lock()
THREAD_REGISTER = dict()

# import system


class QueueEntry(list):
    """
    This class describe a queue entry object to be place on an inqueue of a thread
    """
    def __init__(self, content=None, etype=10, priority=0):
        """

        :param content:
        :param etype: type of the entry : 10: msg, 0: exit
        :param priority: priority of the entry 0=HIGHER, 9=LOWER
        :return:
        """
        list.__init__(self, (etype+priority, content))
        self.etype = etype
        self.priority = priority
        self.content = content


class VikingThread(threading.Thread):
    """
    This class provide a generic thread object for the project
    """

    def __init__(self, name):
        """
        This init method just register the viking thread
        :return:
        """
        if name in THREAD_REGISTER.keys():
            log.error("Thread {0} is already created, aborting".format(name))
            #system.exit_on_error()
        threading.Thread.__init__(self)
        with THREAD_REGISTER_LOCK:
            log.debug("Creating new thread {0}".format(name))
            THREAD_REGISTER[name] = self
        self.name = name
        self.log = init_log("th_"+name)
        self.inqueue = Queue.PriorityQueue(maxsize=settings.get("sys", "default", "queue_size"))
        self._running = threading.Event()
        self._running.clear()

    def exit(self):
        """
        This function MUST provide an sure way to close the thread
        :return:
        """
        if self.inqueue.full():
            self.log.warning("inqueue full but asked to exit")
            while self.inqueue.full():
                # Removing some elements to make place for exit order
                self.log.raw("pop for make place : {0}".format(self.inqueue.get()))
        self.inqueue.put(QueueEntry(None, 0))
        log.debug("Exiting thread {0}".format(self.name))

    def do_exit(self, msg):
        """
        This method is for closing the thread
        :param msg: QueueEntry
        :return:
        """
        self._running.clear()
        with THREAD_REGISTER_LOCK:
            del THREAD_REGISTER[self.name]
            self.log("removed from register")

    def do_msg(self, msg):
        """
        Ask the thread to work on a message
        :param msg: QueueEntry
        :return:
        """
        self.log.warning("do_msg SHOULD be reimplement per thread, recv : {0}".format(msg))

    def run(self):
        """
        This function allow the thread to act like a Viking Thread and exit when it's required
        :return:
        """
        if self._running.isSet():
            self.log.warning("This thread have already been started, aborting start it again")
            return
        self.log.debug("starting..")
        self._running.set()
        self._on_start()
        while self._running.isSet():
            entry = self.inqueue.get()
            if entry.etype == 0:    # exit
                self.do_exit(entry)
            else:
                # if self.name == "dmxmod":
                #     log.debug("tick dmxmod, len queue {0}".format(self.inqueue.qsize()))
                self.do_msg(entry)
        self._on_close()
        self.log.debug("stopped")

    def _on_start(self):
        pass

    def _on_close(self):
        pass



def quit_all_threads():
    global THREAD_REGISTER
    th_list = THREAD_REGISTER.values()         # protect mutable dict (exit thread remove them from list)
    for th in th_list:
        log.debug("asking thread {0} to quit ".format(th.name))
        th.exit()
        th.join()
