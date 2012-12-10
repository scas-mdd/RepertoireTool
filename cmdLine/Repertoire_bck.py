#!/usr/bin/env python
import sys, os
import argparse
from path_builder import PathBuilder
import rep_model
from vcs_types import VcsTypes

class RepCmdLine():
    def __init__(self):
        self.model = rep_model.RepModel()


class customAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None,
                 model=None):
        argparse.Action.__init__(self,
                                 option_strings=option_strings,
                                 dest=dest,
                                 nargs=nargs,
                                 const=const,
                                 default=default,
                                 type=type,
                                 choices=choices,
                                 required=required,
                                 help=help,
                                 metavar=metavar,
                                 )

        self.model = model



    def __call__(self, parser, namespace, values, option_string=None):
        print '%r %r %r' % (namespace, values, option_string)
        setattr(namespace, self.dest, values)
        if option_string == '-o':
			self.model.setProjDir(namespace.dstPath)
        if option_string == '-c':
			self.model.setCcfxPath(namespace.ccfxPath)
        if option_string == '-b':
			self.model.setCcfxTokenSize(40)
        if option_string == '-d':
            for path in namespace.projPaths:
                path = path.rstrip(os.sep)
                self.model.setDiffPath(path)
        if option_string == '-r':
            path = namespace.dirPath[0]
            if not os.path.isdir(path):
                print "Please provide a valid directory"
                return
            for dir in os.listdir(path):
                diff_dir = path + os.sep + dir
                if not os.path.isdir(diff_dir):
                    print diff_dir + " is not a directory"
                else:
 #                   print diff_dir
                    self.model.setDiffPath(diff_dir)
'''
		v.model.setVcsWhich(PathBuilder.Proj0, VcsTypes.Hg)
		# year - month - day
		v.model.setVcsWhen(PathBuilder.Proj0, datetime(2009, 4, 1), datetime(2009, 4, 3))
		v.model.setVcsWhere(PathBuilder.Proj0, '/home/wiley/ws/opensource/OOO340')
		v.model.setVcsSuffix(PathBuilder.Proj0, '.cxx', '.hxx', '.java')

		v.model.setVcsWhich(PathBuilder.Proj1, VcsTypes.Git)
		v.model.setVcsWhere(PathBuilder.Proj1, '/home/wiley/ws/opensource/libreoffice')
		# year - month - day
		v.model.setVcsWhen(PathBuilder.Proj1, datetime(2009, 4, 1), datetime(2009, 4, 3))
		v.model.setVcsSuffix(PathBuilder.Proj1, '.cxx', '.hxx', '.java')
'''


if __name__ == "__main__":

	cfgFile = ""
	rpm = rep_model.RepModel()

	if(len(sys.argv) < 2):
		print "Usage: please give cfg file name"
		sys.exit()

	cfgFile = sys.argv[1]
#	print cfgFile

	f = open(cfgFile, 'r')
	for line in f:
#		print line
		line = line.rstrip("\n")
		if(line.startswith("OUTPUT_DIR")):
				out_dir = line.split("OUTPUT_DIR = ")[1]
				print out_dir
				rpm.setProjDir(out_dir)
		if(line.startswith("CCFX_DIR")):
				ccfx_dir = line.split("CCFX_DIR = ")[1]
				print ccfx_dir
				rpm.setCcfxPath(ccfx_dir)
		if(line.startswith("TOKEN_SIZE")):
				token_size = line.split("TOKEN_SIZE = ")[1]
				print token_size
				rpm.setCcfxTokenSize(token_size)
		if(line.startswith("PROJ0_DIR")):
				proj0 = line.split("PROJ0_DIR = ")[1]
				print "proj0 = " + proj0
				rpm.setVcsWhich(PathBuilder.Proj0, VcsTypes.NoType)
				rpm.setVcsWhere(PathBuilder.Proj0, proj0)
		if(line.startswith("PROJ1_DIR")):
				proj1 = line.split("PROJ1_DIR = ")[1]
				print "proj1 = " + proj1
				rpm.setVcsWhich(PathBuilder.Proj1, VcsTypes.NoType)
				rpm.setVcsWhere(PathBuilder.Proj1, proj1)
		if(line.startswith("SUFFIX")):
				suffix = line.split("SUFFIX = ")[1]
				suf =  suffix.split(",")
				print suf
				rpm.setVcsSuffix(PathBuilder.Proj0, suf[0],suf[1],suf[2])
				rpm.setVcsSuffix(PathBuilder.Proj1, suf[0],suf[1],suf[2])


	print "===\n" + str(rpm)
	sys.exit()
'''
    app = RepCmdLine()
    rpm = app.model

    parser = argparse.ArgumentParser(description='Repertoire command line utility')
    parser.add_argument('--version', action='version', version='Repertoire 1.0')
    parser.add_argument('-o',action=customAction, dest="dstPath",  model=rpm, help="directory to store outputs, default is current-directory")
    parser.add_argument('-c',action=customAction, dest="ccfxPath", model=rpm, help="ccFinder input format")
    parser.add_argument('-b',action=customAction, dest="token",    model=rpm, help="ccFinder token size")
    parser.add_argument('-d', nargs='+',action=customAction,dest="projPaths",model=rpm,help="source project directories which needs to be analyzed")
 #   parser.add_argument('-r', nargs=1,action=customAction,dest="dirPath",model=rpm,
 #                       help="recursively call all the input diff directories to convert them to ccFinder input format")

    args = parser.parse_args()
    print "===\n" + str(rpm)
    sys.exit()

    for proj,path in rpm.path.items():
        print "processing diffs @ %s" % (path)
        if rpm.outPath is None:
            outPath = os.getcwd()
        else:
            outPath = rpm.outPath

        outPath += os.sep + os.path.basename(path)
        rpm.setTmpDirectory(outPath)
        rpm.setSuffixes('java','cpp','h')
        msg,val = rpm.processDiffs(proj,path)
        print "msg = " + msg
        print "value = " + str(val)
        if(val is True):
            rpm.runCCFinderSelf(proj,path)
        print msg
'''

#    if rpm.isProcessDiff is True:
#        print "processing diffs"
#        if rpm.tmpPath is None:
#            rpm.setTmpDirectory(os.getcwd())
#        rpm.setSuffixes('java','cpp','h')
#        msg,val = rpm.processDiffs()
#        print msg
#    sys.exit()

