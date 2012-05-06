import os
import subprocess

from datetime import datetime
from path_builder import LangDecider, PathBuilder
from vcs_interface import VcsInterface
from vcs_types import Commit, VcsTypes
from multiprocessing.pool import ThreadPool


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
        date_range = '"{0} to {1}"'.format(
                self.timeBegin.strftime("%Y-%m-%d"),
                self.timeEnd.strftime("%Y-%m-%d")
                )
        hg_cmd = ('hg log --template=' +
                '"{author|user}\\n{date|isodate}\\n{node|short}\\n{files}\\n"' +
                ' --date ' + date_range)
        # grab the authors, dates, hashes, and files out of the log
        log_process = subprocess.Popen(
                hg_cmd,
                shell=True,
                cwd=self.repoPath,
                stdout=subprocess.PIPE)
        line = log_process.stdout.readline()
        while line:
            c = Commit(VcsTypes.Hg)
            author = line.strip()
            date_line = log_process.stdout.readline().strip()
            c.date = datetime.strptime(
                    date_line[0:len(date_line) - 6], "%Y-%m-%d %H:%M" )
            c.id = log_process.stdout.readline().strip()
            files = log_process.stdout.readline().strip().split()
            line = log_process.stdout.readline()
            for f in files:
                if not self.langDecider.isCode(f):
                    continue
                c.files[f] = None

            if (len(c.files) > 0 and
                    c.date <= self.timeEnd and
                    c.date >= self.timeBegin):
                self.commits.append(c)
        log_process.kill()

    def dumpCommits(self):
        p = ThreadPool(VcsInterface.NumDumpingThreads)
        p.map(lambda c: dump_commit((self, c)), self.commits)

def dump_commit(args):
    old_self, c = args
    dmp_cmd = 'cd {3} && hg diff -c {0} -U 5 {1} > {2}'
    for f in c.files.keys():
        lang = old_self.langDecider.getLang(f)
        suff = old_self.langDecider.getSuffixFor(lang)
        # why? because we've already filtered these diffs implicitly
        path = (old_self.pb.getFilterOutputPath(old_self.proj, lang) +
                ("%09d" % old_self.filesSeen.getInc()) +
                suff)
        print path
        os.system(dmp_cmd.format(c.id, f, path, old_self.repoPath))
        if not os.path.exists(path):
            print 'diff for file {0} from commit {1} produced nothing?'
            c.files.pop(f)
        elif os.path.getsize(path) < 1:
            print 'Ignoring file {0} in commit {1} (empty)'.format(
                    f, c.id)
            c.files.pop(f)
            os.remove(path)
        else:
            c.files[f] = path

def runtest():
    pb = PathBuilder('/home/wiley/tmp')
    g = HgInterface(PathBuilder.Proj0, pb)
    print str(g.setSuffixes('.cxx', '.hxx', '.java'))
    print str(g.setRepoRoot('/home/wiley/ws/opensource/OOO340'))
    print str(g.setTimeWindow(datetime(2011, 1, 1), datetime(2011, 1, 10)))
    print 'loading commits'
    g.load()
    print 'loaded {0} commits'.format(g.commits)
    print 'dumping commits'
    g.dumpCommits()
