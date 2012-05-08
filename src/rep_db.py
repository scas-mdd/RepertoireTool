class FileMeta:
    def __init__(self, diff_file, orig_file, num_edits, num_ports):
        self.diffFile = diff_file
        self.origFile = orig_file
        self.numEdits = num_edits
        self.numPorts = num_ports

    def __repr__(self):
        return "{0},{1},{2},{3}".format(
                self.diffFile,self.origFile,self.numEdits,self.numPorts)

class CommitMeta:
    Proj0 = 0
    Proj1 = 1
    # commit id is (for instance) the hash of the git commit
    # or the svn commit number
    def __init__(self, author, date, commit_id, files, proj_id):
        self.author = author
        self.date = date
        self.commitId = commit_id
        # files is a mapping from fileId to FileMeta
        self.files = files
        # either 0 or 1 (CommitMeta.Proj0 or CommitMeta.Proj1)
        self.projId = proj_id

    def __repr__(self):
        return "{0},{1},{2},{3}\t{4}".format(
                self.projId,self.commitId,self.date,self.author,self.files)

class SideOfClone:
    # file_id is the unique identifier from CCFinder output
    # it really represents a particular file in a particular commit
    def __init__(self, file_id, start_line, end_line):
        self.fileId = file_id
        self.startLine = start_line
        self.endLine = end_line

    def __repr__(self):
        return "{0}.{1}-{2}".format(self.fileId,self.startLine,self.endLine)

    def get_val(self):
        return (self.fileId,self.startLine,self.endLine)

class CloneMeta:
	# lhs and rhs are SideOfClone's
    def __init__(self, clone_id=0, lhs=None, lhs_commit_id=0, rhs=None, rhs_commit_id=0, metric=0):
        self.cloneId = clone_id
        self.lhs = lhs
        self.lhsCommitId = lhs_commit_id
        self.rhs = rhs
        self.rhsCommitId = rhs_commit_id
        self.metric = metric

    def __repr__(self):
        return "{0}\t({1}){2}\t({3}){4}\t{5}".format(
                self.cloneId,self.lhsCommitId,self.lhs,self.rhsCommitId,self.rhs,self.metric)


class RepDB:
    def __init__(self, commits, clones):
        # a mapping from commitId to CommitMeta
        self.commits = commits
        # a list of clones
        self.clones = clones

    def __repr__(self):
        return "[RepDB: {0} and {1}]".format(self.commits, self.clones)

    def getCommitMeta(self,commit_id):
        return self.commits.get(commit_id,None)

    def getCommitDate(self,commit_id):
        commit_meta = self.commits.get(commit_id,None)
        if commit_meta is not None:
            return commit_meta.date
        else:
            return None

    def getCommitAuthor(self,commit_id):
        commit_meta = self.commits.get(commit_id,None)
        if commit_meta is not None:
            return commit_meta.author
        else:
            return None

    def getProjId(self,commit_id):
        commit_meta = self.commits.get(commit_id,None)
        if commit_meta is not None:
            return commit_meta.projId
        else:
            return None

    def getTotalEdit(self,commit_id):
        commit_meta = self.commits.get(commit_id,None)
        if commit_meta is None:
            return None
        fileId2Meta = commit_meta.files
        total_edit = 0
        total_port = 0
        for k,v in fileId2Meta.iteritems():
            total_edit += int(v.numEdits)
        return total_edit

    def getFileName(self,commit_id,file_id):
        commit_meta = self.commits.get(commit_id,None)
        if commit_meta is not None:
            fileId2Meta = commit_meta.files
            file_meta = fileId2Meta.get(file_id,None)
            if file_meta is not None:
                return file_meta.origFile

        return None
