#!/usr/bin/env python
import sys
import pickle

from rep_db import SideOfClone
from rep_db import CloneMeta
from output_parser import RepertoireOutput

def dumpRepOut(rep_out_path, pickle_output_path):
    repOut = RepertoireOutput()
    repOut.loadFromFile(rep_out_path,1)
    clones = []

    for cloneIdx, (clone1, clone2, metric) in repOut.getCloneIter():
        fidx1, start1, end1 = clone1
        fidx2, start2, end2 = clone2

        lhs = SideOfClone(fidx1,start1,end1)
        rhs = SideOfClone(fidx2,start2,end2)

        lhs_commit_id = fidx1 #for time being
        rhs_commit_id = fidx2 #for time being

        ClMeta = CloneMeta(cloneIdx,lhs,lhs_commit_id,rhs,rhs_commit_id,metric)
        clones.append(ClMeta)

    pickle.dump( clones, open( pickle_output_path, "wb" ) )


if __name__ == "__main__":
    if (len(sys.argv) < 3):
         print "Usage: myPickle.py rep_out.txt pickle.txt"
         print "rep_out.txt is the output from repertoire"
         print "pickle output file"
         sys.exit(2)

    rep_out = sys.argv[1]
    pickle_out = sys.argv[2]

    dumpRepOut(rep_out,pickle_out)
