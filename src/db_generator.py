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
        # a mapping from ccfx input file path -> file idx
        # note that since we're loading a ton of output files
        # these indices are necessarily being rewritten
        file2fidx = {}
        # a mapping from fidx -> num ported lines in the corresponding file
        fidx2numports = {}
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
            self.firstPass(output_tuple.output, clones, file2fidx, fidx2numports)

        # map from commit id -> CommitMeta
        commits = {}
        fidx2commitid = {}
        for vcs in (vcs1, vcs2):
            vcs.populateDB(commits, fidx2commitid, file2fidx, fidx2numports)

        # at this point, we have clones filled out, except that we need commit
        # ids for files involved and the # ports per commit haven't been filled
        # out
        for clone in clones:
            if not clone.lhs.fileId in fidx2commitid:
                print "Going down looking for fidx {0} ({1})".format(
                        clone.lhs.fileId, file2fidx[clone.lhs.fileId])
            if not clone.rhs.fileId in fidx2commitid:
                print "Going down looking for fidx {0} ({1})".format(
                        clone.rhs.fileId, file2fidx[clone.rhs.fileId])

            clone.lhsCommitId = fidx2commitid[clone.lhs.fileId]
            clone.rhsCommitId = fidx2commitid[clone.rhs.fileId]

        return RepDB(commits, clones)


    def firstPass(self, output, clones, file2fidx, fidx2numports):
        # maps from the indices as given in output to our rewritten indices
        out_fidx2fidx = {}
        for out_idx, f in output.files.iteritems():
            fidx = len(file2fidx)
            if f in file2fidx:
                fidx = file2fidx[f]
            file2fidx[f] = fidx
            out_fidx2fidx[out_idx] = fidx
            if not (fidx in fidx2numports):
                fidx2numports[fidx] = 0

        for out_clone_idx, clone_pair in output.clones.iteritems():
            cidx = len(clones)
            fidx1 = out_fidx2fidx[clone_pair.clone1.fidx]
            fidx2 = out_fidx2fidx[clone_pair.clone2.fidx]
            clone1 = SideOfClone(
                    fidx1,
                    clone_pair.clone1.start,
                    clone_pair.clone1.end)
            clone2 = SideOfClone(
                    fidx2,
                    clone_pair.clone2.start,
                    clone_pair.clone2.end)
            clone_meta = CloneMeta(
                    cidx,
                    clone1,
                    -1, # we'll fill these in later
                    clone2,
                    -1, # we'll fill these in later
                    clone_pair.metric)
            fidx2numports[fidx1] = fidx2numports[fidx1] + clone_pair.metric
            fidx2numports[fidx2] = fidx2numports[fidx2] + clone_pair.metric
            clones.append(clone_meta)

