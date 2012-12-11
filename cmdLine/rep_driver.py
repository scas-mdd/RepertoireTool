import time

from ccfx_entrypoint import CCFXEntryPoint
from ccfx_input_conv import CCFXInputConverter
from ccfx_output_conv import convert_ccfx_output
from path_builder import PathBuilder, LangDecider
from rep_db import FileMeta, CommitMeta, SideOfClone, CloneMeta, RepDB
from db_generator import RepDBPopulator
import pickle

class RepDriver():
    def __init__(self,model):
        self.proj0 = model.getProj(PathBuilder.Proj0)
        self.proj1 = model.getProj(PathBuilder.Proj1)
        self.path_builder = model.getPathBuilder()
        self.converter = CCFXInputConverter()
        self.ccfx = CCFXEntryPoint(self.path_builder, model.getCcfxPath(), model.getCcfxTokenSize())

    def ccfxConvert(self):
        print "Converting diffs to ccfx compatible format"
        proj0_repo = self.proj0.getRepoRoot()
        proj1_repo = self.proj1.getRepoRoot()
        print proj0_repo
        print proj1_repo
        self.path_builder.setExtDiffPath(0,proj0_repo)
        self.path_builder.setExtDiffPath(1,proj1_repo)

        self.converter.convertExtDiffs(self.path_builder)

    def runCCFX_old(self):
        print "Running ccFinder for old files, this will take quite some time..."
        have_old_c = self.ccfx.processPairs(LangDecider.CXX, False)

        print"Filtering ccFinder old  output based on operation..."
        if have_old_c:
            is_new = False
            lang = LangDecider.CXX
            output = convert_ccfx_output(self.path_builder, lang, is_new)
            rep_out_path = self.path_builder.getRepertoireOutputPath(lang, is_new)
            rep_out_file = self.path_builder.getRepertoireOutputFileName(lang, is_new)
            output.writeToFile(rep_out_path + rep_out_file)

    def runCCFX_new(self):

        print"Running ccFinder for new files, this will take quite some time..."
        have_new_c = self.ccfx.processPairs(LangDecider.CXX, True)

        print "Filtering ccFinder new  output based on operation..."
        if have_new_c:
            is_new = True
            lang = LangDecider.CXX
            output = convert_ccfx_output(self.path_builder, lang, is_new)
            rep_out_path = self.path_builder.getRepertoireOutputPath(lang, is_new)
            rep_out_file = self.path_builder.getRepertoireOutputFileName(lang, is_new)
            output.writeToFile(rep_out_path + rep_out_file)

    def runCCFX(self):
#        self.runCCFX_old()
        self.runCCFX_new()

    def process(self,rep_model):
        msg, success = self.processImpl(rep_model)


    def processImpl(self,model):
        proj0 = model.getProj(PathBuilder.Proj0)
        proj1 = model.getProj(PathBuilder.Proj1)
        path_builder = model.getPathBuilder()
        converter = CCFXInputConverter()
        ccfx = CCFXEntryPoint(path_builder, model.getCcfxPath(), model.getCcfxTokenSize())

        step = 0
        total_steps = 20.0
        final_status = False

		# step == 0:
        print "Loading version histories for first project" + str(step / total_steps)
        step += 1
        proj0.load()

        print "Loading version histories for second project" + str(step / total_steps)
        step += 1
        proj1.load()

        print "Dumping commits for first project" + str(step / total_steps)
        step += 1
        proj0.dumpCommits()

        print "Dumping commits for second project" + str(step / total_steps)
        step += 1
        proj1.dumpCommits()

        print "Converting diffs to ccfx compatible format" + str(step / total_steps)
        step += 1
        converter.convert(path_builder)

        print "Running ccFinder for old C, this will take quite some time..." + str(step / total_steps)
        step += 1
        have_old_c = ccfx.processPairs(LangDecider.CXX, False)

        print"Running ccFinder for new C, this will take quite some time..." + str(step / total_steps)
        step += 1
        have_new_c = ccfx.processPairs(LangDecider.CXX, True)

        print"Running ccFinder for old headers, this will take quite some time..." + str(step / total_steps)
        step += 1
        have_old_h = ccfx.processPairs(LangDecider.HXX, False)

        print"Running ccFinder for new headers, this will take quite some time..." + str(step / total_steps)
        step += 1
        have_new_h = ccfx.processPairs(LangDecider.HXX, True)

        print"Running ccFinder for old Java, this will take quite some time..." + 	str(step / total_steps)
        step += 1
        have_old_j = ccfx.processPairs(LangDecider.JAVA, False)

        print"Running ccFinder for new Java, this will take quite some time..." + str(step / total_steps)
        step += 1
        have_new_j = ccfx.processPairs(LangDecider.JAVA, True)

        print"Filtering ccFinder old C output based on operation..." + str(step / total_steps)
        step += 1
        if have_old_c:
            is_new = False
            lang = LangDecider.CXX
            output = convert_ccfx_output(path_builder, lang, is_new)
            rep_out_path = path_builder.getRepertoireOutputPath(lang, is_new)
            rep_out_file = path_builder.getRepertoireOutputFileName(lang, is_new)
            output.writeToFile(rep_out_path + rep_out_file)

        print "Filtering ccFinder new C output based on operation..." + str(step / total_steps)
        step += 1
        if have_new_c:
            is_new = True
            lang = LangDecider.CXX
            output = convert_ccfx_output(path_builder, lang, is_new)
            rep_out_path = path_builder.getRepertoireOutputPath(lang, is_new)
            rep_out_file = path_builder.getRepertoireOutputFileName(lang, is_new)
            output.writeToFile(rep_out_path + rep_out_file)

        print "Filtering ccFinder old header output based on operation..." + str(step / total_steps)
        step += 1
        if  have_old_h:
            is_new = False
            lang = LangDecider.HXX
            output = convert_ccfx_output(path_builder, lang, is_new)
            rep_out_path = path_builder.getRepertoireOutputPath(lang, is_new)
            rep_out_file = path_builder.getRepertoireOutputFileName(lang, is_new)
            output.writeToFile(rep_out_path + rep_out_file)

        print "Filtering ccFinder new header output based on operation..." + str(step / total_steps)
        step += 1
        if have_new_h:
            is_new = True
            lang = LangDecider.HXX
            output = convert_ccfx_output(path_builder, lang, is_new)
            rep_out_path = path_builder.getRepertoireOutputPath(lang, is_new)
            rep_out_file = path_builder.getRepertoireOutputFileName(lang, is_new)
            output.writeToFile(rep_out_path + rep_out_file)

        print "Filtering ccFinder old java output based on operation..." + str(step / total_steps)
        step += 1
        if not have_old_j:
            is_new = False
            lang = LangDecider.JAVA
            output = convert_ccfx_output(path_builder, lang, is_new)
            rep_out_path = path_builder.getRepertoireOutputPath(lang, is_new)
            rep_out_file = path_builder.getRepertoireOutputFileName(lang, is_new)
            output.writeToFile(rep_out_path + rep_out_file)

        print "Filtering ccFinder new java output based on operation..." + str(step / total_steps)
        step += 1
        if not have_new_j:
            is_new = True
            lang = LangDecider.JAVA
            output = convert_ccfx_output(path_builder, lang, is_new)
            rep_out_path = path_builder.getRepertoireOutputPath(lang, is_new)
            rep_out_file = path_builder.getRepertoireOutputFileName(lang, is_new)
            output.writeToFile(rep_out_path + rep_out_file)

        print "Combining ccFinder output into a unified database..." + str(step / total_steps)
        step += 1
        pickle.dump(model, open(path_builder.getModelPathAndName(), 'w'))
        rep_populator = RepDBPopulator(path_builder)
        db = rep_populator.generateDB(proj0, proj1)
        db_file = open(path_builder.getDBPathAndName(), 'w')
        pickle.dump(db, db_file)
        db_file.close()

        final_status = True

        if final_status:
            return 'Success!', final_status
        return 'Aborting', final_status
