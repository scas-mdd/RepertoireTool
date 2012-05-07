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

    # we add entries to the first two arguments, that's the populate part
    # commits is a mapping from commitId to CommitMeta
    # fidx2commitid is a mapping from file idx to commitId
    # file2fileIdx is a mapping from ccfx input files to the corresponding
    # ccfx file index in the output
    def populateDB(self, commits, fidx2commitid, file2fileIdx):
        for c in self.commits:
            files = {}
            for orig_name, dump_name in c.files.items():
                input_name = self.pb.translateFilterToCCFXInput(dump_name)
                num_edits = count_diff_edits(dump_name)
                # some one else will come through and fill this out later
                num_ports = 0
                file_meta = FileMeta(dump_name, orig_name, num_edits, num_ports)
                file_idx = file2fileIdx[input_name]
                fidx2commitid[file_idx] = c.getDecoratedId()
                files[file_idx] = file_meta
            commit_meta = CommitMeta(c.author, c.date, c.getDecoratedId(), files, c.proj)
            commits[c.getDecoratedId()] = commit_meta

def count_diff_edits(path):
    in_diff = False
    num_edits = 0
    with open(path, 'r') as f:
        for line in f:
            if in_diff:
                if (line.startswith('+') or
                        line.startswith(' ') or
                        line.startswith('-')):
                    num_edits += 1
                elif line.startswith('\\'):
                    pass
                else:
                    in_diff = False
            if line.startswith("@@"):
                in_diff = True
    return num_edits

