import re
import os
from collections import namedtuple

import config

Clone = namedtuple('Clone', ['fidx', 'start', 'end', 'ops'])
ClonePair = namedtuple('ClonePair', ['clone1', 'clone2', 'metric'])
Operation = namedtuple('Operation', ['line', 'op'])

class RepertoireOutput:
    def __init__(self):
        # a map from fileIdx -> filePath
        self.files = {}
        # a map from cloneIdx -> ClonePair
        self.clones = {}

    def loadFromFile(self, input_path, is_rep = False):
        reading_indices = False
        reading_clones = False
        rseparator = re.compile("[.-]")
        clones = set()
        inf = open(input_path, 'r')
        for line in inf:
            if line.startswith("source_files {"):
                reading_indices = True
                continue
            elif line.startswith("clone_pairs {"):
                reading_clones = True
                continue
            elif line.startswith("}"):
                reading_indices = reading_clones = False
            if not (reading_indices or reading_clones):
                continue

            if reading_indices:
                idx,path,sz = line.split("\t")
                self.files[int(idx)] = path
            elif reading_clones:
                if is_rep:
                    idx,clone1,clone2,metric = line.split("\t")
                else:
                    idx,clone1,clone2 = line.split("\t")

                # each clone looks like 1.56-78
                # where 1 is the file index internally consistent
                # 56-78 are the line numbers in the prep file
                fidx1,start1,end1 = rseparator.split(clone1.strip())
                fidx2,start2,end2 = rseparator.split(clone2.strip())
                if fidx1 < fidx2:
                    clone1 = Clone(int(fidx1), int(start1), int(end1), [])
                    clone2 = Clone(int(fidx2), int(start2), int(end2), [])
                else:
                    clone1 = Clone(int(fidx2), int(start2), int(end2), [])
                    clone2 = Clone(int(fidx1), int(start1), int(end1), [])

                if is_rep:
                    self.clones[int(idx)] = ClonePair(clone1, clone2, int(metric))
                else:
                    self.clones[int(idx)] = ClonePair(clone1, clone2, -1)
        inf.close()

    def loadFromData(self, files, clones):
        self.files = files
        self.clones = clones

    def writeToFile(self, output_path):
        out = open(output_path, 'w')
        out.write("source_files {")
        out.write(os.linesep)
        for k,v in self.files.iteritems():
            out.write("{0}\t{1}\t{2}".format(k, v, 0))
            out.write(os.linesep)
        out.write("}")
        out.write(os.linesep)
        out.write("clone_pairs {")
        out.write(os.linesep)
        for clone_idx, clone_pair in self.clones.iteritems():
            out.write("{0}\t{1}.{2}-{3}\t{4}.{5}-{6}\t{7}".format(clone_idx,
                clone_pair.clone1.fidx,
                clone_pair.clone1.start,
                clone_pair.clone1.end,
                clone_pair.clone2.fidx,
                clone_pair.clone2.start,
                clone_pair.clone2.end,
                clone_pair.metric))
            out.write(os.linesep)
        out.write("}")
        out.write(os.linesep)
        out.close()

    def getFilePath(self, fidx):
        return self.files.get(fidx, None)

    def getFileIter(self):
        return self.files.iteritems()

    def getCloneIter(self):
        return self.clones.iteritems()

