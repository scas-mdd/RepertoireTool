import os
import subprocess
import dateutil.parser

from path_builder import LangDecider
from vcs_types import Commit
from vcs_types import VcsTypes

class GitInterface:
    def __init__(self, proj):
        self.proj = proj
        self.langDecider = None
        self.gitPath = ''
        self.timeBegin = None
        self.timeEnd = None

    @staticmethod
    def VerifyGitRepo(git_path):
        if not os.path.isdir(git_path):
            return False
        git_exists = subprocess.Popen(
                'git version',
                shell=True,
                cwd=git_path,
                ).wait() == 0
        if not git_exists:
            return False
        return True

    def isComplete(self):
        return (self.gitPath and
                self.langDecider and
                self.timeBegin and
                self.timeEnd
                )

    def getVcsType(self):
        return VcsTypes.Git

    def getVcsSuffix(self):
        if not self.langDecider:
            return (LangDecider.CXX_SUFF,
                    LangDecider.HXX_SUFF,
                    LangDecider.JAVA_SUFF)
        return self.langDecider.getSuffix()

    def getRepoRoot(self):
        return self.gitPath

    def getVcsWhen(self):
        return (self.timeBegin, self.timeEnd)

    def setSuffixes(self, c_suff, h_suff, j_suff):
        self.langDecider = LangDecider(c_suff, h_suff, j_suff)
        return True

    def setRepoRoot(self, git_path):
        if not GitInterface.VerifyGitRepo(git_path):
            return False
        self.gitPath = git_path
        return True

    def setTimeWindow(self, earliest_time, latest_time):
        self.timeBegin = earliest_time
        self.timeEnd = latest_time
        return True

    # build up self.commits, an array of Commits
    def load(self):
        devnull = open(os.devnull, 'w')
        self.commits = []

        # grab the dates, authors, and hashes out of the log
        log_process = subprocess.Popen(
                'git log --format=" %cn %n %ci %n %H"',
                shell=True,
                cwd=self.gitPath,
                stdout=subprocess.PIPE,
                stderr=devnull
                )
        line = log_process.stdout.readline()
        while line:
            d = Commit(Commit.GIT)
            d.author = line.strip()
            d.date = dateutil.parser.parser(
                    log_process.stdout.readline().strip())
            d.id = log_process.stdout.readline().strip()
            line = log_process.stdout.readline()
            if d.date >= self.timeBegin and d.date <= self.timeEnd:
                self.commits.append(d)


        # now grab the files for each of those commits
        get_files_cmd = 'git show --pretty="format:" --name-only {0}'
        for d in self.commits:
            cmd_inst = get_files_cmd.format(d.id)
            process = subprocess.Popen(
                    cmd_inst,
                    shell=True,
                    cwd=self.gitPath,
                    stdout=subprocess.PIPE,
                    stderr=devnull
                    )
            line = process.stdout.readline()
            while line:
                line = line.strip()
                if len(line) > 0 and self.langDecider.isCode(line):
                    d.files.append(line)
                line = process.stdout.readline()

        idx = 0
        while idx < len(self.commits):
            if len(self.commits[idx].files) < 1:
                # like a remove, but so much faster
                self.commits[idx] = self.commits[len(self.commits) - 1]
            else:
                idx += 1
        devnull.close()

    def dumpCommits(self):
        files_seen = 0
        dmp_cmd = 'git show {0} -- {1}'
        devnull = open(os.devnull, 'w')
        for c in self.commits:
            for f in c.files:
                lang = self.langDecider.getLang(f)
                suff = self.langDescider.getSuffixFor(lang)
                path = self.pb.getDiffPath(self.proj, lang)
                path = path + ("%09d" % files_seen) + suff
                files_seen += 1
                diff_file = open(path, 'w')
                log_process = subprocess.Popen(
                        dmp_cmd.format(c.id, f),
                        shell=True,
                        cwd=self.gitPath,
                        stdout=diff_file,
                        stderr=devnull
                        ).wait()
        devnull.close()

