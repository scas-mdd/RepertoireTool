#!/usr/bin/env python
import os
import sys
import csv
import pickle
from rep_db import *

from clone import Clone
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
        """
        Retrieving info from cloneMeta
        """
        fidx1, start1, end1 = clMeta.lhs.get_val()
        fidx2, start2, end2 = clMeta.rhs.get_val()
        lhs_id = clMeta.lhsCommitId
        rhs_id = clMeta.rhsCommitId
        metric = int(clMeta.metric)
        print "metric = %s" % metric

        if metric == 0:
            continue

        """
        Retrieving info from commitMeta
        """
        #todo: should be refactored in a concided form
        lhs_file, lhs_diff = rep_db.getFileName(lhs_id,fidx1)
        rhs_file, rhs_diff = rep_db.getFileName(rhs_id,fidx2)
        lhs_author = rep_db.getCommitAuthor(lhs_id)
        rhs_author = rep_db.getCommitAuthor(rhs_id)
        lhs_date = rep_db.getCommitDate(lhs_id)
        rhs_date = rep_db.getCommitDate(rhs_id)
        lhs_projid = rep_db.getProjId(lhs_id)
        rhs_projid = rep_db.getProjId(rhs_id)

        lhs_clone = Clone(lhs_projid,lhs_file,lhs_diff,start1,end1,lhs_author,lhs_date)
        rhs_clone = Clone(rhs_projid,rhs_file,rhs_diff,start2,end2,rhs_author,rhs_date)

        if lhs_file is None or rhs_file is None:
            continue

        key = (lhs_file,rhs_file)
        val = (metric,lhs_clone,rhs_clone)

        if rep_db.getProjId(lhs_id) == 'proj1':
            key = (rhs_file,lhs_file)
            val = (metric,rhs_clone,lhs_clone)
        if file_dist.has_key(key) == 0 :
            file_dist[key] = []

#        file_dist[key].append("{0}:{1}-{2}\t{3}:{4}-{5}\t{6}".format(lhs_diff,start1,end1,rhs_diff,start2,end2,metric))
        file_dist[key].append(val)

    return file_dist

def gen_scatter_plot(filedist_hash):

    myPlot = scatterPlot()

    myPlot.fileHash = filedist_hash
    for key, value in sorted(filedist_hash.iteritems(), key=lambda (k,v): (v,k)):
        file1,file2 = key
        metric = 0
        print "value"
        print value
        for i in value:
#            metric += int(i.split('\t')[2])
            print i
            metric += int(i[0])

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
#    print fileDist
    gen_scatter_plot(fileDist)

