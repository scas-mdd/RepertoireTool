from datetime import datetime
from path_builder import LangDecider
from vcs_types import VcsTypes
from rep_db import FileMeta, CommitMeta
import os

class VcsInterface:
    NumDumpingThreads = 10
    EnableMultithreadedDump = True

    def __init__(self, proj, path_builder):
        self.proj = proj
        self.pb = path_builder
        self.langDecider = None
        self.repoPath = ''
        self.timeBegin = None
        self.timeEnd = None

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

    def dumpCommits(self):
        if VcsInterface.EnableMultithreadedDump:
            dump_func = self.getDumpFunc()
            from multiprocessing import Pool
            p = Pool(VcsInterface.NumDumpingThreads)
            arg_list = map(lambda x: (x, self.repoPath), self.commits)
            p.map(dump_func, arg_list)
        else:
            for c in self.commits:
                dump_func((c, self.repoPath))

    # Subclasses should override this
    def getDumpFunc(self):
        raise NotImplementedError

    # Subclasses should override this
    def verifyRepoPath(self, path):
        return True

    # Subclasses should override this
    def getVcsType(self):
        return VcsTypes.NoType

    # Subclasses should override this
    def load(self):
        raise NotImplementedError

    # we add entries to the first two arguments, that's the populate part
    # commits is a mapping from commitId to CommitMeta
    # fidx2commitid is a mapping from file idx to commitId
    # file2fileIdx is a mapping from ccfx input files to the corresponding
    # ccfx file index in the output
    def populateDB(self, commits, fidx2commitid, file2fileIdx, fidx2numports):
        for c in self.commits:
            files = {}
            for orig_name, dump_name in c.files.items():
                if not os.path.exists(dump_name):
                    continue
                if not dump_name in file2fileIdx:
                    print 'Populating DB for {0} failed'.format(dump_name)
                    continue
                num_edits = count_diff_edits(dump_name)
                file_idx = file2fileIdx[dump_name]
                num_ports = fidx2numports[file_idx]
                file_meta = FileMeta(dump_name, orig_name, num_edits, num_ports)
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

