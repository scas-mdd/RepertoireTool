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
        git_cmd = ('git log --name-status --pretty=format:"%H %n %cn %n %ci"' +
                ' --since {0} --before {1}').format(
            self.timeBegin.strftime("%Y-%m-%d"),
            self.timeEnd.strftime("%Y-%m-%d")
            )

        log_process = subprocess.Popen(
                git_cmd,
                shell=True,
                cwd=self.repoPath,
                stdout=subprocess.PIPE)

        line = 'dummy'
        files_seen = 0
        while line:
            c = Commit(VcsTypes.Git)
            hash_line = log_process.stdout.readline()
            author_line = log_process.stdout.readline()
            date_line = log_process.stdout.readline()
            if not hash_line.strip():
                break

            c.id = hash_line.strip()
            c.author = author_line.strip()
            if date_line.strip():
                last_date = datetime.strptime(
                        date_line.strip()[0: -6], "%Y-%m-%d %H:%M:%S" )
            c.date = last_date
            line = log_process.stdout.readline()
            while line.strip():
                f = line.strip()[2:].strip()
                if self.langDecider.isCode(f):
                    lang = self.langDecider.getLang(f)
                    suff = self.langDecider.getSuffixFor(lang)
                    # why filtered? because we've already filtered these diffs implicitly
                    path = (self.pb.getFilterOutputPath(self.proj, lang) +
                            ("%09d" % files_seen) +
                            suff)
                    files_seen += 1
                    c.files[f] = path
                line = log_process.stdout.readline()

            if (len(c.files) > 0 and
                    c.date <= self.timeEnd and
                    c.date >= self.timeBegin):
                self.commits.append(c)
        log_process.kill()

    def dumpCommits(self):
        from multiprocessing import Pool
        p = Pool(VcsInterface.NumDumpingThreads)
        arg_list = map(lambda x: (x, self.repoPath), self.commits)
        p.map(dump_commit, arg_list)
        #for c in self.commits:
        #    dump_commit((c, self.repoPath))

def dump_commit(args):
    c, repo_path = args
    dmp_cmd = 'cd {3} && git show -U5 {0} -- {1} > {2}'
    for f in c.files.keys():
        path = c.files[f]
        os.system(dmp_cmd.format(c.id, f, path, repo_path))
        if not os.path.exists(path):
            print 'diff for file {0} from commit {1} produced nothing?'.format(
                    f, c.id)
            c.files.pop(f)
        elif os.path.getsize(path) < 1:
            print 'Ignoring file {0} in commit {1} (empty)'.format(
                    f, c.id)
            c.files.pop(f)
            os.remove(path)

def runtest():
    pb = PathBuilder('/home/wiley/tmp')
    g = GitInterface(PathBuilder.Proj0, pb)
    print str(g.setSuffixes('.cxx', '.hxx', '.java'))
    print str(g.setRepoRoot('/home/wiley/ws/opensource/libreoffice'))
    print str(g.setTimeWindow(datetime(2010, 1, 1), datetime(2010, 1, 2)))
    g.load()


if __name__=='__main__':
    runtest()
