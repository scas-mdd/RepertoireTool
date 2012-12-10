class VcsTypes:
    NoType = 0
    Git = 1
    Svn = 2
    Hg  = 3
    Cvs = 4

class Commit:
    def __init__(self, proj, type=VcsTypes.Git):
        self.proj = proj
        self.id = None
        self.type = type
        self.files = {}
        self.date = None
        self.author = None

    def getDecoratedId(self):
        return '\t'.join((self.proj, self.id))

    def addFile(self, orig_name, dump_name):
        self.files[orig_name] = dump_name

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "[Commit: {0}, {1}, {2}, {3}]".format(
                self.id,
                self.author,
                str(self.date),
                len(self.files)
                )



