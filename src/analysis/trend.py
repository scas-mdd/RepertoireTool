#!/usr/bin/env python
import os
import sys
import csv
import pickle
from rep_db import *
from datetime import *

#from trend_plot import trendObj
from trend_plot import trendPlot
from clone import Clone


import trend_plot

class trendObj:
    def __init__(self,metric,commit_meta=None):
        self.metric = metric
        if commit_meta is not None:
            print commit_meta
            self.commitId = commit_meta.commitId
            self.projId = commit_meta.projId
            self.date = commit_meta.date
            self.author = commit_meta.author

        self.fileDist = {}


    def __repr__(self):
        return "{0}:{1}".format(self.commitId,self.metric)


def showTrend(rep_db):

    cloneList = rep_db.clones
    commitId2Meta = rep_db.commits

    #data points in trend map
    proj0_trend = {} #map between commitId and trendObj
    proj1_trend = {}

    #first create data points for all commit_dates
    for commit_id,commit_meta in commitId2Meta.iteritems():
        commit_date = rep_db.getCommitDate(commit_id)
#        print commit_date
#        print commit_id
        if commit_date is None:
            continue
        proj_trend = proj1_trend

        if rep_db.getProjId(commit_id) == 'proj0':
            proj_trend = proj0_trend
        proj_trend[commit_date] = trendObj(0,commit_meta)

    #populate data points with metric
    for clMeta in cloneList:
        print "================="
        print clMeta
        lhs_id = clMeta.lhsCommitId
        rhs_id = clMeta.rhsCommitId
        metric = int(clMeta.metric)

        lcommit_date = rep_db.getCommitDate(lhs_id)
        rcommit_date = rep_db.getCommitDate(rhs_id)
        print "%s,%s" % (lcommit_date,rcommit_date)

        commit_id = lhs_id
        commit_date = lcommit_date
        if (lcommit_date <= rcommit_date):
            #porting is done to rhs project
            print "l <= r"
            commit_id = rhs_id
            commit_date = rcommit_date

        proj_trend = proj1_trend
        if rep_db.getProjId(commit_id) == 'proj0':
            proj_trend = proj0_trend

        proj_trend[commit_date].metric += metric
        #file mapping
        fidx1, start1, end1 = clMeta.lhs.get_val()
        fidx2, start2, end2 = clMeta.rhs.get_val()
        """
        lhs_file = rep_db.getFileName(lhs_id,fidx1)
        rhs_file = rep_db.getFileName(rhs_id,fidx2)

        if lhs_file is None or rhs_file is None:
            continue

        key = (lhs_file,rhs_file)
        if rep_db.getProjId(lhs_id) == 'proj1':
            key = (rhs_file,lhs_file)

        file_dist = proj_trend[commit_date].fileDist
        if file_dist.has_key(key) == 0 :
            file_dist[key] = 0
        file_dist[key] += metric
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

        file_dist = proj_trend[commit_date].fileDist
        if file_dist.has_key(key) == 0 :
            file_dist[key] = []

        file_dist[key].append(val)


    trnd_plot = trendPlot(proj0_trend,proj1_trend,rep_db)
    trend_plot.draw(trnd_plot)

#---------------testing-----------------#

if __name__ == "__main__":
    if (len(sys.argv) < 2):
         print "Usage: trend.py rep_out.p"
         print "rep_out.p is pickle dump of rep output"
         sys.exit(2)

    print "trend.py: repertoire database: " + sys.argv[1]

    rep_db = pickle.load(open(sys.argv[1],"rb"))


    fileDist = showTrend(rep_db)

