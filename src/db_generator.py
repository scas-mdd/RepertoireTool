from collections import namedtuple
import os

from path_builder import PathBuilder
from vcs_interface import VcsInterface
from rep_db import FileMeta, CommitMeta, SideOfClone, CloneMeta, RepDB
from output_parser import RepertoireOutput, Clone, ClonePair, Operation

OutputTuple = namedtuple("OutputTuple", ["lang", "is_new", "output"])

class RepDBPopulator:
    def __init__(self, path_builder):
        self.pb = path_builder

    def generateDB(self, vcs1, vcs2):
        # a mapping from file_idx -> ccfx input file path
        # note that since we're loading a ton of output files
        # these indices are necessarily being rewritten
        self.files = {}
        # a list of CloneMeta
        # once again, we're rewriting indices for the very same reasons
        clones = []

        output_tuples = []
        for is_new in [False, True]:
            for lang in ['cxx', 'hxx', 'java']:
                ccfx_output_path = (
                        self.pb.getRepertoireOutputPath(lang, is_new) +
                        self.pb.getRepertoireOutputFileName(lang, is_new))
                if not os.path.exists(ccfx_output_path):
                    continue
                output = RepertoireOutput()
                output.loadFromFile(ccfx_output_path, True)
                output_tuples.append(OutputTuple(lang, is_new, output))

        for output_tuple in output_tuples:
            self.firstPass(output_tuple.output, clones)

        # map from commit id -> CommitMeta
        commits = {}
        # inverted version of self.files
        fidx2file = {v:k for k,v in self.files.iteritems()}
        fidx2commitid = {}
        for vcs in (vcs1, vcs2):
            vcs.populateDB(commits, fidx2commitid, fidx2file)

        # at this point, we have clones filled out, except that we need commit
        # ids for files involved
        for clone in clones:
            clone.lhsCommitId = fidx2commitid[clone.lhs.fileId]
            clone.rhsCommitId = fidx2commitid[clone.rhs.fileId]

        return RepDB(commits, clones)


    def firstPass(self, output, clones):
        output.loadFromFile(ccfx_output_path, True)
        # maps from the indices as given in output to our rewritten indices
        out_fidx2fidx = {}
        for out_idx, f in output.files.iteritems():
            fidx = len(self.files)
            self.files[fidx] = f
            out_fidx2fidx[out_idx] = fidx

        for out_clone_idx, clone_pair in output.clones.iteritems():
            cidx = len(clones)
            clone1 = SideOfClone(
                    out_fidx2fidx[clone_pair.clone1.fidx],
                    clone_pair.clone1.start,
                    clone_pair.clone1.end)
            clone2 = SideOfClone(
                    out_fidx2fidx[clone_pair.clone2.fidx],
                    clone_pair.clone2.start,
                    clone_pair.clone2.end)
            clone_meta = CloneMeta(
                    cidx,
                    clone1,
                    -1, # we'll fill these in later
                    clone2,
                    -1, # we'll fill these in later
                    clone_pair.metric)
            clones.append(clone_meta)

