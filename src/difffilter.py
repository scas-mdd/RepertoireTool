import os

class DiffFilter:
    def __init__(self, extension):
        self.fileEnding = '.' + extension + os.linesep

    def filterDiffs(self, proj, lang, lang_decider, path_builder):
        src_dir = path_builder.getDiffPath(proj, lang)
        dst_dir = path_builder.getFilterOutputPath(proj, lang)

        for i, file_name in enumerate(os.listdir(src_dir)):
            input_path = src_dir + file_name
            output_path = dst_dir + file_name
            (ok, got_some) = self.filterDiff(input_path, output_path)
            if not ok:
                return False
        return True

    def filterDiff(self, inpath, outpath):
        print ">>>>>> filterDiff: inpath = %s, outpath = %s\n" % (inpath, outpath)
        gotsome = False
        oneago=''
        valid=False
        sentinel = (
                '==================================' +
                '=================================' +
                os.linesep)
        try:
            inf = open(inpath, 'r')
            outf = open(outpath, 'w')

            for currline in inf:
                if (currline == sentinel and oneago.startswith('Index: ')) or oneago.startswith('diff --git'):
                    # we're at the start of a new diff section
                    if oneago.endswith(self.fileEnding):
                        # oneago is the index line
                        valid=True
                    else:
                        valid=False
                if valid:
                    gotsome = True
                    outf.write(oneago)
                oneago=currline
            # the above loop misses the last line when its valid
            if valid:
                gotsome = True
                outf.write(oneago)
            inf.close()
            outf.close()
        except IOError:
            return (False, gotsome)
        return (True, gotsome)
