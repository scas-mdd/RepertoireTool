import os
import subprocess
from datetime import datetime

from path_builder import LangDecider, PathBuilder
from vcs_types import Commit, VcsTypes
from vcs_interface import VcsInterface

class NoInterface(VcsInterface):
    def __init__(self, proj, path_builder):
        VcsInterface.__init__(self, proj, path_builder)
        self.commits = []

    @staticmethod
    def VerifyNoRepo(git_path):
        if not os.path.isdir(git_path):
            return False
        return True

    def getVcsType(self):
        return VcsTypes.NoType

    def verifyRepoPath(self, path):
        return NoInterface.VerifyNoRepo(path)

    def load(self):
		return

    def getDumpFunc(self):
        return

def dump_commit(args):
	return

def runtest():
    pb = PathBuilder('/home/bray/tmp')
    g = NoneInterface(PathBuilder.Proj0, pb)
    print str(g.setSuffixes('.cxx', '.hxx', '.java'))
    print str(g.setRepoRoot('/home/bray/SPA/BSDs/FreeBSD/diffs/src_sys_dev'))
#    print str(g.setTimeWindow(datetime(2010, 1, 1), datetime(2010, 1, 2)))
#    g.load()


if __name__=='__main__':
    runtest()
