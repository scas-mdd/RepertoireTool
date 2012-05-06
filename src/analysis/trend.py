#!/usr/bin/env python
import os
import sys
import csv
import pickle
from rep_db import SideOfClone
from rep_db import CloneMeta

#import ternd_plot



def showTrend(rep_out_file):
    cloneList = pickle.load(open(rep_out_file,"rb"))

    fid1ToMetric = {}
    fid2ToMetric = {}

    for clMeta in cloneList:
        clIdx = clMeta.cloneId
        fidx1 = clMeta.lhs.fileId
        fidx2 = clMeta.rhs.fileId
        metric = clMeta.metric

        #this will be later filtered by date
        if fidx1 < fidx2 :
            #this is for projId 1
            if(fid1ToMetric.has_key(fidx1) == 0):
                fid1ToMetric[fidx1] = 0
            fid1ToMetric[fidx1] += int(metric)
        else:
            #this is for projId 2
            if(fid2ToMetric.has_key(fidx1) == 0):
                fid2ToMetric[fidx1] = 0
            fid2ToMetric[fidx1] += int(metric)

    data1 = ["project 1",]
    data2 = ["project 2",]

    for key,val in fid1ToMetric.items():
        data1.append(val)

    for key,val in fid2ToMetric.items():
        data2.append(val)

    print data1
    print data2



#---------------testing-----------------#

if __name__ == "__main__":
    if (len(sys.argv) < 2):
         print "Usage: trend.py rep_out.p"
         print "rep_out.p is pickle dump of rep output"
         sys.exit(2)

    rep_out = sys.argv[1]

    fileDist = showTrend(rep_out)
#    gen_scatter_plot(fileDist)

