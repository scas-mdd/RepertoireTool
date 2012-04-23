from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from threading import Condition
from threading import Lock
import time

from path_builder import PathBuilder, LangDecider
from ccfx_input_conv import CCFXInputConverter
from ccfx_entrypoint import CCFXEntryPoint

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


    def processImpl(self, model):
        proj0 = model.getProj(PathBuilder.Proj0)
        proj1 = model.getProj(PathBuilder.Proj1)
        path_builder = model.getPathBuilder()
        converter = CCFXInputConverter()
        ccfx = CCFXEntryPoint(path_builder, model.getCcfxPath(), model.getCcfxTokenSize())

        step = 0
        total_steps = 20.0
        final_status = False
        while not self.sync.stopRequested():
            if step == 0:
                self.progress("Loading version histories for first project",
                        step / total_steps)
                step += 1
                proj0.load()
            elif step == 1:
                self.progress("Loading version histories for second project",
                        step / total_steps)
                step += 1
                proj1.load()
            elif step == 2:
                self.progress("Dumping commits for first project",
                        step / total_steps)
                step += 1
                proj0.dumpCommits()
                step += 1
            elif step == 3:
                self.progress("Dumping commits for second project",
                        step / total_steps)
                proj1.dumpCommits()
            elif step == 4:
                self.progress("Converting diffs to ccfx compatible format for first project",
                        step / total_steps)
                step += 1
                converter.convert(path_builder)
            elif step == 5:
                self.progress("Converting diffs to ccfx compatible format for second project",
                        step / total_steps)
                step += 1
            elif step == 6:
                self.progress("Running ccFinder for old C, this will take quite some time...",
                        step / total_steps)
                step += 1
                ccfx.processPairs(LangDecider.CXX, False)
            elif step == 7:
                self.progress("Running ccFinder for new C, this will take quite some time...",
                        step / total_steps)
                step += 1
                ccfx.processPairs(LangDecider.CXX, True)
            elif step == 8:
                self.progress("Running ccFinder for old headers, this will take quite some time...",
                        step / total_steps)
                step += 1
                ccfx.processPairs(LangDecider.HXX, False)
            elif step == 9:
                self.progress("Running ccFinder for new headers, this will take quite some time...",
                        step / total_steps)
                step += 1
                ccfx.processPairs(LangDecider.HXX, True)
            elif step == 10:
                self.progress("Running ccFinder for old Java, this will take quite some time...",
                        step / total_steps)
                step += 1
                ccfx.processPairs(LangDecider.JAVA, False)
            elif step == 11:
                self.progress("Running ccFinder for new Java, this will take quite some time...",
                        step / total_steps)
                step += 1
                ccfx.processPairs(LangDecider.JAVA, True)
            else:
                final_status = True
                break

        if final_status:
            return 'Success!', final_status
        return 'Aborting', final_status



