#!/usr/bin/python

import sys
import os
import csv
from optparse import OptionParser
from path_builder import PathBuilder
import shutil

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

class CCFXInputConverter:
    oldConvWriter = None
    newConvWriter = None
    oldCodeFile   = None
    newCodeFile   = None
    oldDstLineNum = 0
    newDstLineNum = 0
    convWriter = None
    dstLineNum = 0

    # process the argument line so the ccFinder can detect clone
    def process_line(self, line, srcLineNum, changeId):
        Operations = Enum(['ADD','DELETE','MODIFIED','NOCHANGE'])
        # default to NOCHANGE
        operation = Operations.NOCHANGE

        temp_line = line
        if (line.startswith('====') or line.startswith('RCS') or
            line.startswith('retrieving') or line.startswith('diff') or
            line.startswith('***') or line.startswith('---') or
            line.startswith('@@') or line.startswith('+++')):
#            line.startswith('@@') or line.startswith('+++') or line.strip().startswith('* ')):
            return
        elif line.startswith('!'):
            temp_line = line.partition('!')[2]
            operation = Operations.MODIFIED
        elif line.startswith('+'):
            temp_line = line.partition('+')[2]
            operation = Operations.ADD
        elif line.startswith('-'):
            temp_line = line.partition('-')[2]
            operation = Operations.DELETE
        else:
            temp_line = line[1:]

        if operation == Operations.NOCHANGE or operation == Operations.ADD:
            self.newCodeFile.writelines(temp_line)
            self.newDstLineNum += 1
            self.newConvWriter.writerow(
                    [self.newDstLineNum, srcLineNum, operation, changeId])
        if operation == Operations.NOCHANGE or operation == Operations.DELETE:
            self.oldCodeFile.writelines(temp_line)
            self.oldDstLineNum += 1
            self.oldConvWriter.writerow(
                    [self.oldDstLineNum, srcLineNum, operation, changeId])

    # reportProgress is a function that takes no arguments
    def convert(self, path_builder, reportProgress = None):

        for proj in [PathBuilder.PROJ0, PathBuilder.PROJ1]:
            for lang in ['cxx', 'hxx', 'java']:
                input_path = path_builder.getFilterOutputPath(proj, lang)
                print "input path : " + input_path
                old_conv_path = path_builder.getLineMapPath(proj, lang, False)
                new_conv_path = path_builder.getLineMapPath(proj, lang, True)
                old_cc_path = path_builder.getCCFXInputPath(proj, lang, False)
                new_cc_path = path_builder.getCCFXInputPath(proj, lang, True)
                shutil.rmtree(old_conv_path, ignore_errors=True)
                shutil.rmtree(new_conv_path, ignore_errors=True)
                shutil.rmtree(old_cc_path, ignore_errors=True)
                shutil.rmtree(new_cc_path, ignore_errors=True)
                os.mkdir(old_conv_path)
                os.mkdir(new_conv_path)
                os.mkdir(old_cc_path)
                os.mkdir(new_cc_path)
                for input_file in os.listdir(input_path):
                    print input_file
                    inf = open(input_path + input_file, 'r')
                    self.oldCodeFile = open(old_cc_path + input_file, 'w')
                    self.newCodeFile = open(new_cc_path + input_file, 'w')
                    oldConv = open(old_conv_path +
                                path_builder.makeLineMapFileName(input_file), 'w')
                    self.oldConvWriter = csv.writer(oldConv,delimiter=',')
                    newConv = open(new_conv_path + path_builder.makeLineMapFileName(input_file), 'w')
                    self.newConvWriter = csv.writer(newConv,delimiter=',')
                    self.oldConvWriter.writerow(
                            ['Target Line Number',
                            'Original Line Number',
                            'Operation', 'Change Id'
                            ])
                    self.newConvWriter.writerow(
                            ['Target Line Number',
                                'Original Line Number',
                                'Operation',
                                'Change Id'
                                ])
                    self.oldDstLineNum = 0
                    self.newDstLineNum = 0

                    searching = False
                    changeId = 0
                    fileName = ''
                    last_idx = -1
                    for idx, line in enumerate(inf):
                        print line
                        last_idx = idx
                        if (not searching and
                            not (line.startswith(' ') or
                                line.startswith('+') or
                                line.startswith('-') or
                                line.startswith("\\"))):
                            # -+ and space are obvious, but there are some
                            # diffs with a line "\ No newline at end of file"
                            # or something similar
                            # which is apparently valid output
                            searching = True
                            firstSearchingLine = True

                        if searching:
                            if line.startswith('---'):
                                # diffs have the old file path in this line
                                fileName = line[4:]
                                firstSearchingLine = False
                            if line.startswith('@@'):
                                # diffs start real content with @@
                                searching = False
                                changeId += 1
                                firstSearchingLine = False
                            if firstSearchingLine:
                                self.oldConvWriter.writerow([fileName])
                                self.newConvWriter.writerow([fileName])
                                temp_line = (
                                        "/* --- " +
                                        line.partition("\n")[0] +
                                        " --- */" +
                                        "\n"
                                        )
                                self.oldCodeFile.writelines(temp_line)
                                self.newCodeFile.writelines(temp_line)
                                self.oldDstLineNum += 1
                                self.newDstLineNum += 1

                            firstSearchingLine = False
                            continue

                        # all line numbers are 1 based (not 0)
                        self.process_line(line, idx + 1, changeId)

                    if last_idx == -1:
                        print 'bad one: ' + input_file
                    inf.close()
                    self.oldCodeFile.close()
                    self.newCodeFile.close()
                    oldConv.close()
                    newConv.close()
                    if not reportProgress is None:
                        reportProgress()


    '''
    convertExtDiffs is specific to BSD diffs right now
    '''
    def convertExtDiffs(self, path_builder,reportProgress = None):

        count = 0
        lang = "cxx"

        for proj in [PathBuilder.PROJ0, PathBuilder.PROJ1]:
            #for lang in [PathBuilder.jSuff, PathBuilder.cSuff,PathBuilder.hSuff]:
            print proj
            count += 1
            diff_path = path_builder.getExtDiffPath(count-1);
            if diff_path is None:
                break
            for lang in ['java', 'cxx', 'h']:
                input_path = path_builder.getFilterOutputPath(proj, lang)
                old_conv_path = path_builder.getLineMapPath(proj, lang, False)
                new_conv_path = path_builder.getLineMapPath(proj, lang, True)
                old_cc_path = path_builder.getCCFXInputPath(proj, lang, False)
                new_cc_path = path_builder.getCCFXInputPath(proj, lang, True)
                shutil.rmtree(old_conv_path, ignore_errors=True)
                shutil.rmtree(new_conv_path, ignore_errors=True)
                shutil.rmtree(old_cc_path, ignore_errors=True)
                shutil.rmtree(new_cc_path, ignore_errors=True)
                os.mkdir(old_conv_path)
                os.mkdir(new_conv_path)
                os.mkdir(old_cc_path)
                os.mkdir(new_cc_path)

                print count
                diff_path = path_builder.getExtDiffPath(count-1);
                print diff_path
                for input_file in os.listdir(diff_path):
                    print input_file
                    inf = open(diff_path + os.sep + input_file, 'r')
                    input_file = input_file + "." + lang
                    self.oldCodeFile = open(old_cc_path + input_file, 'w')
                    self.newCodeFile = open(new_cc_path + input_file, 'w')
                    oldConv = open(old_conv_path +
                                path_builder.makeLineMapFileName(input_file), 'w')
                    self.oldConvWriter = csv.writer(oldConv,delimiter=',')
                    newConv = open(new_conv_path + path_builder.makeLineMapFileName(input_file), 'w')
                    self.newConvWriter = csv.writer(newConv,delimiter=',')
                    self.oldConvWriter.writerow(
                            ['Target Line Number',
                            'Original Line Number',
                            'Operation', 'Change Id'
                            ])
                    self.newConvWriter.writerow(
                            ['Target Line Number',
                                'Original Line Number',
                                'Operation',
                                'Change Id'
                                ])
                    self.oldDstLineNum = 0
                    self.newDstLineNum = 0

                    srcFile = False
                    changeId = 0
                    fileName = ''
                    last_idx = -1

                    for idx, line in enumerate(inf):
                        last_idx = idx
                        #cvs specific
                        if line.startswith("Index:"):
                            fileName = line[7:].strip()
    #                        fileName = "\"" + fileName + "\""
                            fileExtension = os.path.splitext(fileName)[1].strip()
    #                        print fileExtension
                            '''
                            if ((fileExtension == ".c")
                                    or (fileExtension == ".h")
									or (fileExtension == ".java")
									or (fileExtension == ".cpp")):
                                    '''
                            if (fileExtension == ("." + lang)):
                                print fileName
                                changeId += 1
                                firstSearchingLine = False
                                self.oldConvWriter.writerow([fileName])
                                self.newConvWriter.writerow([fileName])
                                temp_line = (
                                        "/* --- " +
                                        fileName +
                                        " --- */" +
                                        "\n"
                                        )
                                self.oldCodeFile.writelines(temp_line)
                                self.newCodeFile.writelines(temp_line)
                                self.oldDstLineNum += 1
                                self.newDstLineNum += 1
                                srcFile = True
                                continue
                            else:
                                srcFile = False

                        if srcFile:
                            self.process_line(line, idx + 1, changeId)

                    if last_idx == -1:
                        print 'bad one: ' + input_file
                    inf.close()
                    self.oldCodeFile.close()
                    self.newCodeFile.close()
                    oldConv.close()
                    newConv.close()
                    if not reportProgress is None:
                        reportProgress()


