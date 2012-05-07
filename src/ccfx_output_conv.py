import os
from path_builder import PathBuilder
from output_parser import RepertoireOutput, ClonePair, Clone, Operation
from operation_filter import opFilter

import config

class CCFXMetaData:
    # this is a little complex, so we're writing a nice comment about it
    # 1. we start with big aggregate diff files between versions
    # 2. we then filter those big diff files by language in files like 0027.c
    # 3. ccfx needs c-ish looking input, so we remove the diff metadata
    # 4. we save a mapping between lines in the diff and lines in the ccfx input
    # 5. ccfx processes the file, spitting out a metadata file per input file
    # 6. we use the metadata file, the output from ccfx, and our own mapping
    #    to build a datastructure that saves how lines in different diffs (2)
    #    are clones of other lines in other diffs (2)
    #
    # ccfx_input        == path to a file from 3
    # ccfx_preprocessed == path to a file from 5
    # filter_conv       == path to a file from 4
    # fitler_output     == path to a file from 2
    def __init__(self, ccfx_input, ccfx_preprocessed, filter_conv, filter_output):
        self.ccfxInput = ccfx_input
        self.ccfxPrep  = ccfx_preprocessed
        self.filterConv = filter_conv
        self.filterOutput = filter_output

class CCFXMetaMapping:
    def __init__(self):
        self.name2meta = {}

    def addFile(self, meta):
        self.name2meta[meta.ccfxInput] = meta

    def getMetas(self):
        return self.name2meta.values()

    def getMetaForPath(self, input_path):
        return self.name2meta.get(input_path, None)

    def hasInputPath(self, input_path):
        return not self.getMetaForPath is None

def convert_ccfx_output(pb, lang, is_new, debug = False):
    metaDB = CCFXMetaMapping()
    # maps from ccfx input paths to meta objects representing the files
    for proj in [PathBuilder.PROJ0, PathBuilder.PROJ1]:
        filter_path = pb.getFilterOutputPath(proj, lang)
        conv_path   = pb.getLineMapPath(proj, lang, is_new)
        ccfx_i_path = pb.getCCFXInputPath(proj, lang, is_new)
        ccfx_p_path = pb.getCCXFPrepPath(proj, lang, is_new)
        for name in os.listdir(filter_path):
            meta = CCFXMetaData(
                    ccfx_i_path + name,
                    ccfx_p_path + pb.findPrepFileFor(ccfx_p_path, name),
                    conv_path + pb.makeLineMapFileName(name),
                    filter_path + name)
            metaDB.addFile(meta)

    # we have our files, now map line numbers in the prep files to input files
    for meta in metaDB.getMetas():

        if config.DEBUG is True:
            print "prep file = " + meta.ccfxPrep
            print "conv file = " + meta.filterConv

        prepHandler = open(meta.ccfxPrep, 'r')
        prep = prepHandler.readlines()
        prepHandler.close()

        convHandler = open(meta.filterConv, 'r')
        conv = convHandler.readlines()
        convHandler.close()

        input2orig = {}
        pidx2orig = {}
        origline2op = {}
        # build a map of line numbers in ccfx_input to filtered diff line
        last_dst = last_src = 0
        for i, cline in enumerate(conv):
            if i < 2:
                continue
            if  cline.rstrip().startswith('"'): #filename-->skip the line
                continue

            dstIdx,srcIdx,op,changId = cline.split(',')
            input2orig[int(dstIdx)] = int(srcIdx)
            origline2op[int(srcIdx)] = op
            last_dst = int(dstIdx) + 1
            last_src = int(srcIdx) + 1
        # ccfx cares about the end of file, which isn't represented by our mappings
        input2orig[last_dst] = last_src
        origline2op[last_src] = "NOCHANGE"
        for pidx, pline in enumerate(prep):
            inputIdx = int(pline.partition(".")[0], 16)
            # ccfx output has numbers like 0-131, meaning that pidx
            # is meant to be taken from 0
            pidx2orig[pidx] = input2orig.get(inputIdx, -1)
            if debug and input2orig.get(inputIdx, -1) == -1:
                print "failed to translate from pidx to original: {0} -> {1}".format(pidx, inputIdx)
                print "    file: " + meta.ccfxInput

        meta.prepIdx2OrigIdx = pidx2orig
        meta.line2op = origline2op

    ccfx_out_path = pb.getCCFXOutputPath() + pb.getCCFXOutputFileName(
            lang, is_new, is_tmp = False)
    ccfx_out = RepertoireOutput()
    if debug:
        print 'loading from ccfx output file: {0}'.format(ccfx_out_path)
    ccfx_out.loadFromFile(ccfx_out_path)
    if debug:
        print "finished loading ccfx output."

    files = {}
    for fileIdx, path in ccfx_out.getFileIter():
        if not metaDB.hasInputPath(path):
            raise Exception(
                    "Couldn't find meta information for file: {0}".format(
                        path))
        meta = metaDB.getMetaForPath(path)
        files[fileIdx] = meta.filterOutput

    clones = {}

    # rewrite the line numbers to index into filter_output files
    for clone_idx, clone_pair in ccfx_out.getCloneIter():
        fidx1, start1, end1, op1 = clone_pair.clone1
        fidx2, start2, end2, op2 = clone_pair.clone2
        metric = clone_pair.metric
        meta1 = metaDB.getMetaForPath(ccfx_out.getFilePath(fidx1))
        meta2 = metaDB.getMetaForPath(ccfx_out.getFilePath(fidx2))

        start1 = meta1.prepIdx2OrigIdx.get(start1 + 1, -1)
        end1 = meta1.prepIdx2OrigIdx.get(end1, -1)
        start2 = meta2.prepIdx2OrigIdx.get(start2 + 1, -1)
        end2 = end2 = meta2.prepIdx2OrigIdx.get(end2, -1)

        if (start1 == -1 or start2 == -1 or
                end1 == -1 or end2 == -1):
            if debug:
                print 'line translation failed for ' + str(clone_pair)
            # don't even try to translate a clonew with bad indices
            # this usually means we somehow dumped an empty file on
            # ccfx and we can't translate the eof token correctly
            # enabling debug should verify this
            continue


        for i in range(start1, end1 + 1):
            op = meta1.line2op.get(i, "X")
            op1.append(Operation(i,op))

        for i in range(start2, end2 + 1):
            op = meta2.line2op.get(i, "X")
            op2.append(Operation(i,op))


        clone1 = Clone(fidx1, start1, end1, op1)
        clone2 = Clone(fidx2, start2, end2, op2)
        if clone1.fidx < clone2.fidx:
            unsplit_clone = ClonePair(clone1, clone2, metric)
        else:
            unsplit_clone = ClonePair(clone2, clone1, metric)

        # split into hunks, add those hunks into our final output
        clone_pairs = split_clone_into_hunks(unsplit_clone, debug)
        for clone_pair in clone_pairs:
            clones[len(clones)] = clone_pair


    rep_out = RepertoireOutput()
    rep_out.loadFromData(files, clones)
    return rep_out

def split_clone_into_hunks(clone_pair, debug = False):
    clone1 = clone_pair.clone1
    clone2 = clone_pair.clone2
    clones = []

    #First partition the clone regions in contiguous hunk
    #print "operation 1:"
    hunks1 = get_adj_hunk(clone1.ops, debug)
    #print "operation 2:"
    hunks2 = get_adj_hunk(clone2.ops, debug)
    if debug and not (hunks2 and hunks1):
        print 'empty hunks? ' + str(clone_pair)

    if len(hunks1) == len(hunks2):
        for hunk1, hunk2 in zip(hunks1, hunks2):
            start1,end1 = hunk1
            start2,end2 = hunk2
            cl1 = Clone(clone_pair.clone1.fidx, start1, end1, [])
            cl2 = Clone(clone_pair.clone2.fidx, start2, end2, [])
            clones.append(ClonePair(cl1, cl2, clone_pair.metric))
    else:
        #uncommon case:
        # or at least you had better hope its rare, because this logic is
        # not convincing at all
        high = 1
        big_hunks = hunks1
        small_hunks = hunks2
        start = clone2.start
        small_ops = clone2.ops
        if len(hunks1) < len(hunks2):
            high = 2
            big_hunks = hunks2
            small_hunks = hunks1
            start = clone1.start
            small_ops = clone1.ops

        small_start = start
        for big_hunk in big_hunks:
                big_start, big_end = big_hunk
                big_hunk_len = big_end - big_start
                small_end = small_start + big_hunk_len
                if high == 1:
                    cl1 = Clone(clone1.fidx, big_start, big_end, [])
                    cl2 = Clone(clone2.fidx, small_start, small_end, [])
                else:
                    cl1 = Clone(clone1.fidx, small_start, small_end, [])
                    cl2 = Clone(clone2.fidx, big_start, big_end, [])
                clones.append(ClonePair(cl1, cl2, clone_pair.metric))
                index = small_end - start + 1
                while index < len(small_ops) and 'X' == small_ops[index].op:
                    index += 1
                small_start = start + index
    ret = []
    # second filter the hunks w.r.t their operations
    op_filter = opFilter(clone1.ops, clone2.ops)
    for clone_pair in clones:
        metric = op_filter.filterByOp(clone_pair)
        if not metric is None:
            ret.append(ClonePair(clone_pair.clone1, clone_pair.clone2, metric))

    return ret

def get_adj_hunk(ops, debug = False):
    hunks = []
    if len(ops) < 1:
        if debug:
            print 'How did we end up with no ops to get hunks from?'
        return hunks
    start = end = ops[0].line
    is_hunk = True

    for i in range(1,len(ops)):
        if ops[i].op == "X":
            if is_hunk is True:
                hunks.append((start, end))
                is_hunk = False
        else:
            end = ops[i].line
            if is_hunk is False:
                start = end
                is_hunk = True

    hunks.append((start, end))
    return hunks


if __name__ == "__main__":
    path_builder = PathBuilder( "/home/wiley/ws/RepertoireTool/src/repertoire_tmp_1719278194", super_safe_mode = True)
    convert_ccfx_output(path_builder, 'cxx', is_new = False, debug = True)
