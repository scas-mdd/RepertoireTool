#!/usr/bin/env python
import os
import sys
import csv
import pickle
from rep_db import *

from scatter_plot import scatterPlot

def showFileDist(rep_db):

    cloneList = rep_db.clones
#    commitId2Meta = rep_db.commits

    file_dist = {}

    #populate data points with metric
    for clMeta in cloneList:
        print "================="
        print clMeta
        fidx1, start1, end1 = clMeta.lhs.get_val()
        fidx2, start2, end2 = clMeta.rhs.get_val()

        lhs_id = clMeta.lhsCommitId
        rhs_id = clMeta.rhsCommitId
        metric = int(clMeta.metric)

        lhs_file = rep_db.getFileName(lhs_id,fidx1)
        rhs_file = rep_db.getFileName(rhs_id,fidx2)

        if lhs_file is None or rhs_file is None:
            continue

        key = (lhs_file,rhs_file)
        if rep_db.getProjId(lhs_id) == 'proj1':
            key = (rhs_file,lhs_file)
        if file_dist.has_key(key) == 0 :
            file_dist[key] = 0
        file_dist[key] += metric

    return file_dist

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

    fileDist = showFileDist(rep_db)
    gen_scatter_plot(fileDist)

