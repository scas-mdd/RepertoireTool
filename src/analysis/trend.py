#!/usr/bin/env python
import os
import sys
import csv
import pickle
from rep_db import *
from datetime import *

#from trend_plot import trendObj
from trend_plot import trendPlot

import trend_plot

class trendObj:
    def __init__(self,metric,commit_meta=None,file_list=None):
        self.metric = metric
        if commit_meta is not None:
            self.commitId = commit_meta.commitId
            self.projId = commit_meta.projId
            self.date = commit_meta.date
            self.author = commit_meta.author
            self.fileList = file_list

    def __repr__(self):
        return "{0}:{1}".format(self.commitId,self.metric)


def showTrend(rep_db):

    cloneList = rep_db.clones
    commitId2Meta = rep_db.commits

    #data points in trend map
    proj0_trend = {} #map between commitId and trendObj
    proj1_trend = {}

    #first create data points for all commitIds
    for commit_id,commit_meta in commitId2Meta.iteritems():
        print commit_id
        proj_trend = proj1_trend
        if rep_db.getProjId(commit_id) == 'proj0':
            proj_trend = proj0_trend
        proj_trend[commit_id] = trendObj(0,commit_meta)

    #populate data points with metric
    for clMeta in cloneList:
        print clMeta
        clIdx = clMeta.cloneId
        fidx1 = clMeta.lhs.fileId
        fidx2 = clMeta.rhs.fileId
        lhs_id = clMeta.lhsCommitId
        rhs_id = clMeta.rhsCommitId
        metric = clMeta.metric

        lcommit_date = rep_db.getCommitDate(lhs_id)
        rcommit_date = rep_db.getCommitDate(rhs_id)

        print "%s,%s" % (lcommit_date,rcommit_date)

        commit_id = lhs_id
        if (lcommit_date <= rcommit_date):
            #porting is done to rhs project
            commit_id = rhs_id

        proj_trend = proj1_trend
        if rep_db.getProjId(commit_id) == 'proj0':
            proj_trend = proj0_trend

        proj_trend[commit_id].metric += metric

    trnd_plot = trendPlot(proj0_trend,proj1_trend,rep_db)
    trend_plot.draw(trnd_plot)

"""
    trend_plot_data = []
    trend_plot_label0 = []
    trend_plot_label1 = []

    for proj in (proj0_trend,proj1_trend):
        pcent_port = []
        commit_date = []
        commit_id = []
        for cm_id,trnd_obj in proj.iteritems():
            total_edit = rep_db.getTotalEdit(cm_id)
            total_port = trnd_obj.metric
            pcent_edit = (float(total_port)/total_edit)*100
            pcent_port.append(pcent_edit)
        trend_plot_data.append(pcent)

    print pcent_port

    data0 = []
    data1 = []

    for key,val in lproj_trend.items():
        data0.append(val)

    for key,val in rproj_trend.items():
        data1.append(val)

    trnd_obj0 = trendObj("project 0",data0)
    trnd_obj1 = trendObj("project 1",data1)

    trnd_plot = trendPlot()
    trnd_plot.add_obj(trnd_obj0)
    trnd_plot.add_obj(trnd_obj1)

    trend_plot.draw(trnd_plot)

#    print data0
#    print data1

"""

#---------------testing-----------------#

if __name__ == "__main__":
    if (len(sys.argv) < 2):
         print "Usage: trend.py rep_out.p"
         print "rep_out.p is pickle dump of rep output"
         sys.exit(2)

    print "trend.py: repertoire database: " + sys.argv[1]

    rep_db = pickle.load(open(sys.argv[1],"rb"))


    fileDist = showTrend(rep_db)

