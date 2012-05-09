#!/usr/bin/env python
import os
import sys
import csv
import pickle
from rep_db import *

from scatter_plot import scatterPlot
import scatter_plot

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


        lhs_file, lhs_diff = rep_db.getFileName(lhs_id,fidx1)
        rhs_file, rhs_diff = rep_db.getFileName(rhs_id,fidx2)

        if lhs_file is None or rhs_file is None:
            continue

        key = (lhs_file,rhs_file)
        if rep_db.getProjId(lhs_id) == 'proj1':
            key = (rhs_file,lhs_file)
        if file_dist.has_key(key) == 0 :
            file_dist[key] = []
#        file_dist[key] += metric
        file_dist[key].append("{0}:{1}-{2}\t{3}:{4}-{5}\t{6}".format(lhs_diff,start1,end1,rhs_diff,start2,end2,metric))

    return file_dist

def gen_scatter_plot(filedist_hash):

    myPlot = scatterPlot()

    myPlot.fileHash = filedist_hash
    for key, value in sorted(filedist_hash.iteritems(), key=lambda (k,v): (v,k)):
        file1,file2 = key
        metric = 0
        for i in value:
            metric += int(i.split('\t')[2])

        myPlot.set_value(file1,file2,metric)

    scatter_plot.draw(myPlot)


#---------------testing-----------------#

if __name__ == "__main__":
    if (len(sys.argv) < 2):
         print "Usage: trend.py rep_out.pickle"
         print "rep_out.pickle is pickle dump of rep output"
         sys.exit(2)

    print "trend.py: repertoire database: " + sys.argv[1]

    rep_db = pickle.load(open(sys.argv[1],"rb"))

    fileDist = showFileDist(rep_db)
    print fileDist
    gen_scatter_plot(fileDist)

