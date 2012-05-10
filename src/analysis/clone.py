
from rep_db import *

class Clone:
    def __init__(self, proj_id, orig_file, diff_file, start_line, end_line, developer, commit_date):
        self.origFile = orig_file
        self.diffFile = diff_file
        self.startLine = start_line
        self.endLine = end_line
        self.projId = proj_id
        self.dev = developer
        self.commitDate = commit_date

    def __repr__(self):
        return "{0}:{1}:{2}:{3}-{4}\t{5}\t{6}".format(
                self.projId,self.origFile,self.diffFile,
                self.startLine,self.endLine,self.dev,self.commitDate)


