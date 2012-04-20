import os
import subprocess
import dateutil.parser

class Commit:
    GIT = 1
    SVN = 2
    CVS = 3
    def __init__(self, type=GIT, proj):
        self.id = None
        self.type = type
        self.files = []
        self.diffs = {}
        self.date = None
        self.author = None

    def __str__(self):
        return self.__repr__()

        return "[Commit: {0}, {1}, {2}, {3}]".format(
                self.id,
                self.author,
                str(self.date),
                len(self.files)
                )

    def __repr__(self):
        return "[Commit: {0}, {1}, {2}, {3}]".format(
                self.id,
                self.author,
                str(self.date),
                len(self.files)
                )


class GitInterface:
    def __init__(self, lang_decider, git_path, proj):
        self.langDecider = lang_decider
        self.gitPath = git_path
        self.proj = proj


    def verify(self):
        devnull = open(os.devnull, 'w')
        git_exists = subprocess.Popen(
                'git version',
                shell=True,
                stdout=devnull,
                stderr=devnull
                ).wait() == 0
        devnull.close()
        if not git_exists:
            return False
        return True

        # excellent, so now we know we're working in a git repo

    def load(self):
        if not os.path.isdir(self.gitPath):
            return False
        cwd = os.getcwd()
        os.chdir(self.gitPath)
        ret = self.loadImpl()
        os.chdir(cwd)
        return ret

    def dumpCommits(self):
        if not os.path.isdir(self.gitPath):
            return False
        cwd = os.getcwd()
        os.chdir(self.gitPath)
        ret = self.dumpCommitsImpl()
        os.chdir(cwd)
        return ret

    def dumpCommitsImpl(self):
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
                        dmp_cmd.format(c.id, f)
                        shell=True,
                        stdout=diff_file,
                        stderr=devnull
                        ).wait()
        devnull.close()

    # build up self.commits, an array of Commits
    def loadImpl(self):
        devnull = open(os.devnull, 'w')
        self.commits = []

        # grab the dates, authors, and hashes out of the log
        log_process = subprocess.Popen(
                'git log --format=" %cn %n %ci %n %H"',
                shell=True,
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
            self.commits.append(d)
            line = log_process.stdout.readline()

        # now grab the files for each of those commits
        get_files_cmd = 'git show --pretty="format:" --name-only {0}'
        for d in self.commits:
            cmd_inst = get_files_cmd.format(d.id)
            process = subprocess.Popen(
                    cmd_inst,
                    shell=True,
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
        while idx < len(self.commits)
            if len(self.commits[idx].files) < 1:
                # like a remove, but so much faster
                self.commits[idx] = self.commits[len(self.commits) - 1]
            else:
                idx += 1
        devnull.close()

