from datetime import datetime
from threading import Lock
from path_builder import LangDecider
from vcs_types import VcsTypes

class AtomicInt:
    def __init__(self, value = 0):
        self.mutex = Lock()
        self.value = value

    def getInc(self):
        self.mutex.acquire()
        ret = self.value
        self.value += 1
        self.mutex.release()
        return ret

    def get(self):
        self.mutex.acquire()
        ret = self.value
        self.mutex.release()
        return ret


class VcsInterface:
    NumDumpingThreads = 10
    def __init__(self, proj, path_builder):
        self.proj = proj
        self.pb = path_builder
        self.langDecider = None
        self.repoPath = ''
        self.timeBegin = None
        self.timeEnd = None
        self.filesSeen = AtomicInt()

    def isComplete(self):
        return (self.repoPath and
                self.langDecider and
                self.timeBegin and
                self.timeEnd
                )

    def getVcsSuffix(self):
        if not self.langDecider:
            return (LangDecider.CXX_SUFF,
                    LangDecider.HXX_SUFF,
                    LangDecider.JAVA_SUFF)
        return self.langDecider.getSuffix()

    def getRepoRoot(self):
        return self.repoPath

    def getVcsWhen(self):
        return (self.timeBegin, self.timeEnd)

    def setSuffixes(self, c_suff, h_suff, j_suff):
        self.langDecider = LangDecider(c_suff, h_suff, j_suff)
        return True

    def setRepoRoot(self, path):
        if not self.verifyRepoPath(path):
            return False
        self.repoPath = path
        return True

    def getLangDecider(self):
        return self.langDecider

    def setTimeWindow(self, earliest_time, latest_time):
        self.timeBegin = earliest_time
        self.timeEnd = latest_time
        return True

    # Subclasses should override this
    def verifyRepoPath(self, path):
        return True

    # Subclasses should override this
    def getVcsType(self):
        return VcsTypes.NoType

    # Subclasses should override this
    def load(self):
        raise NotImplementedError

    # Subclasses should override this
    def dumpCommits(self):
        raise NotImplementedError

