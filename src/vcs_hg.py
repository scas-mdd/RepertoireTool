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
        files_seen = 0
        line = log_process.stdout.readline()
        while line:
            c = Commit(VcsTypes.Hg)
            author_line = line
            date_line = log_process.stdout.readline().strip()
            hash_line = log_process.stdout.readline().strip()
            date = datetime.strptime(date_line[0:len(date_line) - 6],
                    "%Y-%m-%d %H:%M" )
            c.id = hash_line.strip()
            c.author = author_line.strip()
            c.date = date
            files = log_process.stdout.readline().strip().split()
            line = log_process.stdout.readline()
            for f in files:
                if self.langDecider.isCode(f):
                    lang = self.langDecider.getLang(f)
                    suff = self.langDecider.getSuffixFor(lang)
                    # why filtered? because we've already filtered these diffs implicitly
                    path = (self.pb.getFilterOutputPath(self.proj, lang) +
                            ("%09d" % files_seen) +
                            suff)
                    files_seen += 1
                    c.addFile(f, path)

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
        #    dump_commit((self, c))

def dump_commit(args):
    c, repo_path = args
    dmp_cmd = 'cd {3} && hg diff -c {0} -U 5 {1} > {2}'
    for f in c.files.keys():
        path = c.files[f]
        print path
        os.system(dmp_cmd.format(c.id, f, path, repo_path))
        if not os.path.exists(path):
            print 'diff for file {0} from commit {1} produced nothing?'
            c.files.pop(f)
        elif os.path.getsize(path) < 1:
            print 'Ignoring file {0} in commit {1} (empty)'.format(
                    f, c.id)
            c.files.pop(f)
            os.remove(path)

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
