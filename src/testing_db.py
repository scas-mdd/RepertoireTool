#!/usr/bin/env python
import os
import sys
import pickle

from simple_model import SimpleModel
from path_builder import PathBuilder
from vcs_git import GitInterface
from vcs_hg import HgInterface
from vcs_types import VcsTypes
from db_generator import RepDBPopulator


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'usage: ./testing_db.py path_to_repertoire_root'
        sys.exit(-1)

    db_path = sys.argv[1] + os.sep + 'rep_db.pickle'
    if not os.path.exists(db_path):
        print "can't find db at {0}".format(db_path)
        sys.exit(-1)

    db = pickle.load(open(db_path, 'r'))
    print db
