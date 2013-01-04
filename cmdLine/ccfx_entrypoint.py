import config
import os
from subprocess import Popen, PIPE
from path_builder import PathBuilder

class CCFXEntryPoint:
    def __init__(self, path_builder, ccfx_path = './ccfx', token_sz = 40, file_sep = True, grp_sep = True):
        self.ccfxPath = ccfx_path
        self.tokenSize = token_sz
        self.fileSep = file_sep
        self.grpSep = grp_sep
        self.pb = path_builder

    def processPairs(self, lang, is_new):
        clone_path = self.pb.getCCFXOutputPath()
        path0 = self.pb.getCCFXInputPath(PathBuilder.PROJ0, lang, is_new)
        path1 = self.pb.getCCFXInputPath(PathBuilder.PROJ1, lang, is_new)
        tmp_out = clone_path + self.pb.getCCFXOutputFileName(
                lang, is_new, is_tmp = True)
        out = clone_path + self.pb.getCCFXOutputFileName(
                lang, is_new, is_tmp = False)
        if path1 is None:
            #Only one project
            return self.processDir(path0, tmp_out, out, lang)
        else:
            return self.processPair(path0, path1, tmp_out, out, lang)

    def processDir(self, dir0, tmp_out_path, out_path, lang = 'java'):
        if lang != 'java':
            lang = 'cpp'

        option = "-w "
        option_sep = ""
        if self.fileSep is True: #no intra-file clone
            option += "w-"
        else:
            option += "w+"
        '''
        if self.grpSep: #no intra-group clone
            option += "f-g+"
            option_sep = "-is"
        else:
            option += "f+"
        '''
        cmd_str = (
            '{0} d {1} -dn {2} {3} -b {4} -o {5}'.format(
                self.ccfxPath,
                lang,
                dir0,
                option,
                self.tokenSize,
                tmp_out_path))

        if config.DEBUG is True:
            print cmd_str

        proc = Popen(cmd_str,shell=True,stdout=PIPE,stderr=PIPE)
        proc.wait()
        if proc.returncode != 0:
            print "Couldn't run %s successfully" % (cmd_str)
            print "error code = " + str(proc.returncode)
            return False

        conv_str = '{0} p {1} > {2}'.format(self.ccfxPath, tmp_out_path, out_path)

        if config.DEBUG is True:
            print conv_str
        proc = Popen(conv_str,shell=True,stdout=PIPE,stderr=PIPE)
        proc.wait()
        if proc.returncode != 0:
            print "Couldn't run %s successfully" % (cmd_str)
            print "error code = " + str(proc.returncode)
            return False


        return True

    def processPair(self, dir0, dir1, tmp_out_path, out_path, lang = 'java'):
        if lang != 'java':
            lang = 'cpp'

        option = "-w "
        option_sep = ""
        if self.fileSep is True: #no intra-file clone
            option += "f-"
        else:
            option += "f+"
        if self.grpSep: #no intra-group clone
            option += "w-g+"
            option_sep = "-is"
        else:
            option += "w+"

        cmd_str = (
            '{0} d {1} -dn {2} {3} -dn {4} {5} -b {6} -o {7}'.format(
                self.ccfxPath,
                lang,
                dir0,
                option_sep,
                dir1,
                option,
                self.tokenSize,
                tmp_out_path))

        if config.DEBUG is True:
            print cmd_str

        proc = Popen(cmd_str,shell=True,stdout=PIPE,stderr=PIPE)
        proc.wait()
        if proc.returncode != 0:
            print "Couldn't run %s successfully" % (cmd_str)
            print "error code = " + str(proc.returncode)
            return False

        conv_str = '{0} p {1} > {2}'.format(self.ccfxPath, tmp_out_path, out_path)

        if config.DEBUG is True:
            print conv_str
        proc = Popen(conv_str,shell=True,stdout=PIPE,stderr=PIPE)
        proc.wait()
        if proc.returncode != 0:
            print "Couldn't run %s successfully" % (cmd_str)
            print "error code = " + str(proc.returncode)
            return False


        return True


#./ccfx d cpp -v -dn ~/project-bray/BSD/NetBsd/ccFinderInputFiles_new  -is -dn ~/project-bray/BSD/FreeBsd/ccFinderInputFiles_new -w f-w-g+ -b 70 -o net_free_new_70.ccfxd
#./ccfx p net_free_new_70.ccfxd > net_free_new_70.txt
