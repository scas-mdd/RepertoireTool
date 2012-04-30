import os
import subprocess

from datetime import datetime

from path_builder import LangDecider, PathBuilder
from vcs_interface import VcsInterface
from vcs_types import Commit, VcsTypes


class HgInterface(VcsInterface):
    def __init__(self, proj, path_builder):
        VcsInterface.__init__(self, proj, path_builder)
        self.commits = []

    def __init__(self, proj, path_builder):
        VcsInterface.__init__(self, proj, path_builder)

    @staticmethod
    def VerifyHgRepo(path):
        if not os.path.isdir(path):
            return False
        # this actually prints the directory of the root of the process
        # but i'm not going to check it
        process = subprocess.Popen(
                'hg root',
                shell=True,
                cwd=path,
                )
        if not process.wait() == 0:
            return False
        return True

    def getVcsType(self):
        return VcsTypes.Hg

    def verifyRepoPath(self, path):
        return HgInterface.VerifyHgRepo(path)

    # build up self.commits, an array of Commits
    def load(self):
        self.commits = []

        # grab the authors, dates, hashes, and files out of the log
        log_process = subprocess.Popen(
                'hg log --template="{author|user}\n{rfc822date|date}\n' +
                '{node|short}\n{files}\n"',
                shell=True,
                cwd=self.repoPath,
                stdout=subprocess.PIPE)
        line = log_process.stdout.readline()
        while line:
            c = Commit(VcsTypes.Hg)
            author = line.strip()
            date_line = log_process.stdout.readline().strip()
            c.date = datetime.strptime(
                    date_line[0:len(date_line) - 6], "%a %b %d %H:%M:%S %Y" )
            c.id = log_process.stdout.readline().strip()
            files = log_process.stdout.readline().strip().split()
            line = log_process.stdout.readline()
            if c.date < self.timeBegin or c.date > self.timeEnd:
                continue
            i = 0
            while i < len(files):
                if not files[i] or not self.langDecider.isCode(files[i]):
                    files[i] = files[-1]
                    files.pop()
                else:
                    i += 1
            if len(files) > 0:
                c.files = files
                self.commits.append(c)
        log_process.kill()

    def dumpCommits(self):
        files_seen = 0
        # 5 lines of context
        dmp_cmd = 'hg diff -c {0} -U 5 {1}'
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

