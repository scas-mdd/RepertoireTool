#!/usr/bin/env python
import sys
import pickle
import file_dist as fd




if __name__ == "__main__":
    if (len(sys.argv) < 2):
         print "Usage: trend.py temp.pickle"
         print "temp.pickle is pickle dump of file_hash from trend_plot.py"
         sys.exit(2)

    print "trend.py: repertoire database: " + sys.argv[1]

    fileDist = pickle.load(open(sys.argv[1],"rb"))
    print fileDist

    fd.gen_scatter_plot(fileDist)

