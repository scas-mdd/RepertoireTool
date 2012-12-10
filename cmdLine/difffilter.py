import os

class DiffFilter:
    def __init__(self, extension):
        self.fileEnding = '.' + extension + os.linesep

    def filterDiff(self, inpath, outpath):
#        print ">>>>>> filterDiff: inpath = %s, outpath = %s\n" % (inpath, outpath)
        gotsome = False
        oneago=''
        valid=False
        print ">>> filterDiff >>" + self.fileEnding
        sentinel = (
                '==================================' +
                '=================================' +
                os.linesep)
        sentinel1 = ('==================================');
        try:
            inf = open(inpath, 'r')
            outf = open(outpath, 'w')

            for currline in inf:
                if (currline.startswith(sentinel1) and oneago.startswith('Index:')) or oneago.startswith('diff --git'):
                    # we're at the start of a new diff section
                    #print "oneago =" + oneago
                    if oneago.endswith(self.fileEnding):
                    	print "oneago =" + oneago
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
