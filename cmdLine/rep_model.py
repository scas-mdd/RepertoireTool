import os
import subprocess

from path_builder import PathBuilder
from vcs_git import GitInterface
from vcs_hg import HgInterface
from vcs_none import NoInterface
from vcs_types import VcsTypes

class RepModel:
    def __init__(self):
        self.projDir = ''
#        self.ccfxPath = '/home/bray/SealLab/RepertoireTool1/ccFinder/ccfx'
        self.ccfxPath = ''
        self.ccfxTokenSize = 50
        self.projs = {PathBuilder.Proj0 : None, PathBuilder.Proj1 : None}
        self.pb = None

    def __str__(self):
#		print self.projs[PathBuilder.PROJ0].getRepoRoot()
		class_string = "projDir : " + self.projDir + "\n"
		class_string += "ccfxPath : " + self.ccfxPath + "\n"
		class_string += "ccfxTokenSize : " + str(self.ccfxTokenSize) + "\n"
		class_string += "proj0 : " + str(self.projs[PathBuilder.PROJ0].getRepoRoot()) + "\n"
		class_string += "proj1 : " + str(self.projs[PathBuilder.PROJ1].getRepoRoot()) + "\n"
		return class_string

    @staticmethod
    def ValidateProjDir(path):
        return os.path.isdir(path)

    @staticmethod
    def VerifyCCFinderPath(ccfx_path):
        if not os.path.exists(ccfx_path) or not os.path.isfile(ccfx_path):
            return False
        ccfx_process = subprocess.Popen(
                ccfx_path,
                shell=True,
                stdout=subprocess.PIPE,
                )
        line = ccfx_process.stdout.readline()
        works = False
        if not line is None and line.startswith('CCFinderX ver'):
            works = True
        return works and ccfx_process.wait() == 0

    def getProjDir(self):
        # this is gross because we create a unique directory inside projdir
        return os.path.abspath(os.path.join(self.projDir, os.path.pardir))

    def setProjDir(self, path):
        if not RepModel.ValidateProjDir(path):
            return False
        if self.getProjDir() == path:
            # we've already set up this directory
            return True
        uniq = 'repertoire_tmp_' + str(int(os.times()[4] * 100))
        self.projDir = path + os.sep + uniq
        os.mkdir(self.projDir)
        self.pb = PathBuilder(self.projDir)
        for proj in self.projs.values():
            if not proj:
                continue
            proj.pb = self.pb
        return True

    def setCcfxPath(self, path):
        if not RepModel.VerifyCCFinderPath(path):
            return False
        self.ccfxPath = path
        return True

    def setCcfxTokenSize(self, token_size):
        self.ccfxTokenSize = token_size
        return True

    def getCcfxPath(self):
	return self.ccfxPath

    def getCcfxTokenSize(self):
        return self.ccfxTokenSize

    def setVcsWhere(self, proj, path):
        if proj != PathBuilder.PROJ0 and proj != PathBuilder.PROJ1:
            return False
        if not self.projs[proj]:
            return False
        return self.projs[proj].setRepoRoot(path)





    def setVcsSuffix(self, proj, c_suff, h_suff, j_suff):
        if proj != PathBuilder.PROJ0 and proj != PathBuilder.PROJ1:
            return False
        if not self.projs[proj]:
            return False
        return self.projs[proj].setSuffixes(c_suff, h_suff, j_suff)

    # these should be datetime objects
    def setVcsWhen(self, proj, start, end):
        if proj != PathBuilder.PROJ0 and proj != PathBuilder.PROJ1:
            return False
        if not self.projs[proj]:
            return False
        return self.projs[proj].setTimeWindow(start, end)

    def isComplete(self):
        return (self.projDir and self.ccfxPath and self.ccfxTokenSize and
                self.projs[PathBuilder.Proj0] and
                self.projs[PathBuilder.Proj0].isComplete() and
                self.projs[PathBuilder.Proj1] and
                self.projs[PathBuilder.Proj1].isComplete()
                )



    def getVcsSuffix(self, proj):
        if proj != PathBuilder.PROJ0 and proj != PathBuilder.PROJ1:
            return ('', '', '')
        if not self.projs[proj]:
            return ('', '', '')
        return self.projs[proj].getVcsSuffix()

    def getVcsTimeWindow(self, proj):
        if proj != PathBuilder.PROJ0 and proj != PathBuilder.PROJ1:
            return None, None
        if not self.projs[proj]:
            return None, None
        return self.projs[proj].getVcsWhen()

    def getVcsWhich(self, proj):
        if proj != PathBuilder.PROJ0 and proj != PathBuilder.PROJ1:
            return None
        if not self.projs[proj]:
            return None
        return self.projs[proj].getVcsType()

    def getVcsWhere(self, proj):
        if proj != PathBuilder.PROJ0 and proj != PathBuilder.PROJ1:
            return None
        if not self.projs[proj]:
            return None
        return self.projs[proj].getRepoRoot()

    def getProj(self, proj):
        return self.projs[proj]

    def getPathBuilder(self):
        return self.pb


    def setVcsWhich(self, proj, which_vcs = VcsTypes.Git):
		if proj != PathBuilder.PROJ0 and proj != PathBuilder.PROJ1:
			return False
		if which_vcs == VcsTypes.Git:
			vcs = GitInterface(proj, self.pb)
		elif which_vcs == VcsTypes.Hg:
			vcs = HgInterface(proj, self.pb)
		else:
			vcs = NoInterface(proj, self.pb)
	#		return False

		if (not self.projs[proj] or self.projs[proj].getVcsType() != which_vcs):
			self.projs[proj] = vcs
			return True

