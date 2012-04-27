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

        # grab the dates, authors, and hashes out of the log
        log_process = subprocess.Popen(
                'git log --format=" %cn %n %ci %n %H"',
                shell=True,
                cwd=self.repoPath,
                stdout=subprocess.PIPE)

        line = log_process.stdout.readline()
        while line:
            c = Commit(VcsTypes.Git)
            c.author = line.strip()
            date_line = log_process.stdout.readline().strip()
            c.date = datetime.strptime(
                    date_line[0:len(date_line) - 6], "%Y-%m-%d %H:%M:%S" )
            c.id = log_process.stdout.readline().strip()
            line = log_process.stdout.readline()
            if c.date >= self.timeBegin and c.date <= self.timeEnd:
                self.commits.append(c)
        log_process.kill()

        # now grab the files for each of those commits
        get_files_cmd = 'git show --pretty="format:" --name-only {0}'
        for d in self.commits:
            cmd_inst = get_files_cmd.format(d.id)
            process = subprocess.Popen(
                    cmd_inst,
                    shell=True,
                    cwd=self.repoPath,
                    stdout=subprocess.PIPE)
            raw_line = 'dummy'
            while raw_line:
                raw_line = process.stdout.readline()
                line = raw_line.strip()
                if line and self.langDecider.isCode(line):
                    d.files.append(line)
            process.kill()
        idx = 0
        while idx < len(self.commits):
            if len(self.commits[idx].files) < 1:
                # like a remove, but so much faster
                self.commits[idx] = self.commits[len(self.commits) - 1]
                self.commits.pop()
            else:
                idx += 1

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

def runTest():
    pb = PathBuilder('/home/wiley/tmp')
    g = GitInterface(PathBuilder.Proj0, pb)
    print str(g.setSuffixes('.c', '.h', '.java'))
    print str(g.setRepoRoot('/home/wiley/ws/opensource/cinnamon'))
    print str(g.setTimeWindow(datetime(1970, 1, 1), datetime(2020, 1, 1)))
    g.load()
