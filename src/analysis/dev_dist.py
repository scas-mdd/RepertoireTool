#!/usr/bin/env python
import os
import sys
import pickle
from rep_db import *

from scatter_plot import scatterPlot

def showDevDist(rep_db):

    cloneList = rep_db.clones
#    commitId2Meta = rep_db.commits

    dev_dist = {}

    #populate data points with metric
    for clMeta in cloneList:
        print "================="
        print clMeta
        fidx1, start1, end1 = clMeta.lhs.get_val()
        fidx2, start2, end2 = clMeta.rhs.get_val()

        lhs_id = clMeta.lhsCommitId
        rhs_id = clMeta.rhsCommitId
        metric = int(clMeta.metric)

        lhs_author = rep_db.getCommitAuthor(lhs_id)
        rhs_author = rep_db.getCommitAuthor(rhs_id)

        if lhs_author is None or rhs_author is None:
            continue

        key = (lhs_author,rhs_author)
        if rep_db.getProjId(lhs_id) == 'proj1':
            key = (rhs_author,lhs_author)
        if dev_dist.has_key(key) == 0 :
            dev_dist[key] = 0
        dev_dist[key] += metric

    return dev_dist

def gen_scatter_plot(filedist_hash):

    myPlot = scatterPlot()

    for key, value in sorted(filedist_hash.iteritems(), key=lambda (k,v): (v,k)):
        file1,file2 = key
        myPlot.set_value(file1,file2,value)

    myPlot.draw()


#---------------testing-----------------#

if __name__ == "__main__":
    if (len(sys.argv) < 2):
         print "Usage: trend.py rep_out.pickle"
         print "rep_out.pickle is pickle dump of rep output"
         sys.exit(2)

    print "trend.py: repertoire database: " + sys.argv[1]

    rep_db = pickle.load(open(sys.argv[1],"rb"))

    devDist = showDevDist(rep_db)
    gen_scatter_plot(devDist)

