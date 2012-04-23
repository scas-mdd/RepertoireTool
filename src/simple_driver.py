from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from threading import Condition
from threading import Lock
import time

class StartStopSync:
    def __init__(self):
        self.cv = Condition()
        self.shouldStop = False
        self.shouldStart = False
        self.running = False

    # Blocks until we're sure that we've stopped
    def pleaseStop(self):
        self.cv.acquire()
        self.shouldStop = True
        while self.running:
            self.cv.wait()
        self.shouldStop = False
        self.cv.release()

    # Blocks until we're sure that we've started
    def pleaseStart(self, trigger):
        self.cv.acquire()
        self.shouldStart = True
        trigger()
        while not self.running:
            self.cv.wait()
        self.shouldStart = False
        self.cv.release()

    def stopRequested(self):
        self.cv.acquire()
        ret = self.shouldStop
        self.cv.release()
        return ret

    def setRunning(self, is_running):
        self.cv.acquire()
        self.running = is_running
        self.cv.notifyAll()
        self.cv.release()

class SimpleDriver(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.sync = StartStopSync()

    # called externally, threadsafe, blocks until we stop
    def stopWorking(self):
        self.sync.pleaseStop()

    # called externally, threadsafe, blocks until we start
    # trigger is a function to call that should "trigger" us starting work
    def startWorking(self, trigger):
        self.sync.pleaseStart(trigger)

    # called periodically with status updates
    def progress(self, msg, frac):
        self.emit(QtCore.SIGNAL("progress"), (msg, frac))

    def process(self, simple_model):
        self.sync.setRunning(True)
        msg, success = self.processImpl(simple_model)
        self.sync.setRunning(False)
        self.emit(QtCore.SIGNAL("done"), (msg, success))


    def processImpl(self, simple_model):
        print 'doing work!'
        while not self.sync.stopRequested():
            print 'working'
            time.sleep(1)

        return 'skeleton code', True



