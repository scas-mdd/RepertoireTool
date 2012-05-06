class FileMeta:
	def __init__(self, diff_file, orig_file, num_edits, num_ports):
		self.diffFile = diff_file
		self.origFile = orig_file
		self.numEdits = num_edits
		self.numPorts = num_ports

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

class SideOfClone:
	# file_id is the unique identifier from CCFinder output
	# it really represents a particular file in a particular commit
	def __init__(self, file_id, start_line, end_line):
		self.fileId = file_id
		self.startLine = start_line
		self.endLine = end_line

class CloneMeta:
	# lhs and rhs are SideOfClone's
    def __init__(self, clone_id=0, lhs=None, lhs_commit_id=0, rhs=None, rhs_commit_id=0, metric=0):
        self.cloneId = clone_id
        self.lhs = lhs
        self.lhsCommitId = lhs_commit_id
        self.rhs = rhs
        self.rhsCommitId = rhs_commit_id
        self.metric = metric

class RepDB:
	def __init__(self):
		# a mapping from commitId to CommitMeta
		self.commits = commits
		# a list of clones
		self.clones = clones
