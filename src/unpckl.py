#!/usr/bin/env python
import sys
import pickle
import csv
import re

from rep_db import *


#--------------------------------------------#

def unpckl_commit_meta(commitId2Meta):
    print "Function: unpckl_commit_meta"

    for commit_id,cmMeta in commitId2Meta.iteritems():
        print cmMeta

#--------------------------------------------#

def unpckl_clone_meta(clones):
    print "Function: unpckl_clone_meta"
    for item in clones:
        print item

#--------------------------------------------#

if __name__ == "__main__":


    if (len(sys.argv) < 2):
         print "Usage: trend.py rep_db.p"
         print "rep_db.p is pickle dump of rep database"
         sys.exit(2)

    rep_db = pickle.load(open(sys.argv[1],"rb"))

    commitId2Meta = rep_db.commits
    clones = rep_db.clones

    unpckl_clone_meta(clones)
    unpckl_commit_meta(commitId2Meta)

