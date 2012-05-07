#!/usr/bin/env python
import sys
import pickle
import csv
import re

from rep_db import *

fileId2Meta = {} #map between fileId and FileMeta
commitId2Meta = {} #map between commitId and CommitMeta
clones = []

def pckl_file_meta(file_meta):
    print "Finction: pckl_file_meta"
    ifile  = open(file_meta, "rb")
    reader = csv.reader(ifile)
    global fileId2Meta

    rownum = 0
    for row in reader:
        if rownum is not 0:
            fileMeta = FileMeta(row[1],row[2],row[3],row[4])
            fileId2Meta[row[0]] = fileMeta
        rownum += 1

    ifile.close()

#--------------------------------------------#

def pckl_commit_meta(commit_meta):
    print "Function: pckl_commit_meta"
    column = {
            "commit_id":0,
            "author":1,
            "date":2,
            "file_id":3,
            "proj_id":4
            }
    global fileId2Meta
    global commitId2Meta

    ifile  = open(commit_meta, "rb")
    reader = csv.reader(ifile)

    rownum = 0
    for row in reader:
        if rownum is not 0:
            fm = None
            fileMeta = fileId2Meta.get(row[column["file_id"]],None)
            fm = {row[column["file_id"]]:fileMeta}
            cmMeta = CommitMeta(row[column["commit_id"]],row[column["author"]],row[column["date"]],fm,row[column["proj_id"]])
#            print cmMeta
            commitId2Meta[row[column["commit_id"]]] = cmMeta

        rownum += 1

    ifile.close()


#--------------------------------------------#

def pckl_clone_meta(clone_meta):
    print "Function: pckl_clone_meta"
    column = {
            "clone_id":0,
            "lhs":1,
            "lhsCommitId":2,
            "rhs":3,
            "rhsCommitId":4,
            "metric":5
            }
    global fileId2Meta
    global commitId2Meta
    global clones

    ifile  = open(clone_meta, "rb")
    reader = csv.reader(ifile)

    rownum = 0
    for row in reader:
        if rownum is not 0:
            clone_id = row[0]
            lhs = row[1]
            lhs_id = row[2]
            rhs = row[3]
            rhs_id = row[4]
            metric = row[5]
            rseparator = re.compile("[.-]")
            fidx1,start1,end1 = rseparator.split(lhs.strip())
            fidx2,start2,end2 = rseparator.split(rhs.strip())
            lhs = SideOfClone(fidx1,start1,end1)
            rhs = SideOfClone(fidx2,start2,end2)
            ClMeta = CloneMeta(clone_id,lhs,lhs_id,rhs,rhs_id,metric)
            clones.append(ClMeta)

        rownum += 1

    ifile.close()

#--------------------------------------------#

if __name__ == "__main__":

    pickle_out = sys.argv[1]

    pckl_file_meta("data/fileMeta.csv")
    pckl_commit_meta("data/commitMeta.csv")
    pckl_clone_meta("data/cloneMeta.csv")

    global commitId2Meta
    global clones

    rep_db = RepDB()
    rep_db.commits = commitId2Meta
    rep_db.clones = clones

    pickle.dump( rep_db, open( pickle_out, "wb" ) )
