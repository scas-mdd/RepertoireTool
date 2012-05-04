import os
import subprocess
from datetime import datetime

from path_builder import LangDecider, PathBuilder
from vcs_types import Commit, VcsTypes
from vcs_interface import VcsInterface

class GitInterface(VcsInterface):
    def __init__(self, proj, path_builder):
        VcsInterface.__init__(self, proj, path_builder)
        self.commits = []

    @staticmethod
    def VerifyGitRepo(git_path):
        if not os.path.isdir(git_path):
            return False
        # this actually prints the directory of the root of the process
        # but i'm not going to check it
        process = subprocess.Popen(
                'git rev-parse --show-toplevel',
                shell=True,
                cwd=git_path,
                )
        if not process.wait() == 0:
            return False
        return True

    def getVcsType(self):
        return VcsTypes.Git

    def verifyRepoPath(self, path):
        return GitInterface.VerifyGitRepo(path)

    # build up self.commits, an array of Commits
    def load(self):
        self.commits = []

        # git command produces output like
        #0992e5111fcac424e3b0e944a077716428ab4f84
        # Julien Nabet
        #  2012-04-30 19:50:19 +0200
        #  M       canvas/source/null/null_canvasfont.cxx
        #  M       canvas/source/null/null_canvasfont.hxx
        #  M       canvas/source/null/null_canvashelper.cxx
        #  M       canvas/source/null/null_canvashelper.hxx
        #  M       unusedcode.easy
        log_process = subprocess.Popen(
                'git log --name-status --pretty=format:"%H %n %cn %n %ci"',
                shell=True,
                cwd=self.repoPath,
                stdout=subprocess.PIPE)

        line = 'dummy'
        while line:
            c = Commit(VcsTypes.Git)
            c.id = log_process.stdout.readline().strip()
            c.author = log_process.stdout.readline().strip()
            date_line = log_process.stdout.readline().strip()
            if date_line:
                last_date = datetime.strptime(
                        date_line[0:len(date_line) - 6], "%Y-%m-%d %H:%M:%S" )
            c.date = last_date
            line = log_process.stdout.readline()
            files = []
            while line.strip():
                line = line.strip()[2:].strip()
                if self.langDecider.isCode(line):
                    c.files.append(line)
                line = log_process.stdout.readline()

            if (len(c.files) > 0 and
                    c.date <= self.timeEnd and
                    c.date >= self.timeBegin):
                self.commits.append(c)
        log_process.kill()

    def dumpCommits(self):
        files_seen = 0
        dmp_cmd = 'git show -U5 {0} -- {1}'
        for c in self.commits:
            for f in c.files:
                lang = self.langDecider.getLang(f)
                suff = self.langDecider.getSuffixFor(lang)
                # why? because we've already filtered these diffs implicitly
                path = (self.pb.getFilterOutputPath(self.proj, lang) +
                        ("%09d" % files_seen) +
                        suff)
                files_seen += 1
                diff_file = open(path, 'w')
                log_process = subprocess.Popen(
                        dmp_cmd.format(c.id, f),
                        shell=True,
                        cwd=self.repoPath,
                        stdout=diff_file).wait()
                diff_file.close()

def runtest():
    pb = PathBuilder('/home/wiley/tmp')
    g = GitInterface(PathBuilder.Proj0, pb)
    print str(g.setSuffixes('.cxx', '.hxx', '.java'))
    print str(g.setRepoRoot('/home/wiley/ws/opensource/libreoffice'))
    print str(g.setTimeWindow(datetime(2011, 1, 1), datetime(2012, 1, 1)))
    g.load()


if __name__=='__main__':
    runtest()
