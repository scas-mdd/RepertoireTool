#!/usr/bin/env python
import sys, os
import argparse
from path_builder import PathBuilder
import rep_model
from vcs_types import VcsTypes
from rep_driver import RepDriver


if __name__ == "__main__":

	cfgFile = ""
	rpm = rep_model.RepModel()

	if(len(sys.argv) < 2):
		print "Usage: please give cfg file name"
		sys.exit()

	cfgFile = sys.argv[1]

	f = open(cfgFile, 'r')
	for line in f:
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
   	rd = RepDriver(rpm)
#	rd.process(rpm)
	rd.ccfxConvert()
	rd.runCCFX()

	sys.exit()
