import os
import shutil
from threading import RLock
from difffilter import DiffFilter

class PathBuilder:
    PROJ0 = 'proj0'
    PROJ1 = 'proj1'
    Proj0 = PROJ0
    Proj1 = PROJ1

    # pass in a path to a directoy we have all to ourselves
    def __init__(self, root, force_clean = False, super_safe_mode = False):
        self.root = root
        self.mutex = RLock()
        self.superSafeMode = super_safe_mode
        if force_clean:
            for f in os.listdir(self.root):
                # doesn't clean out normal files, but I'll let it slide
                shutil.rmtree(self.root + os.sep + f, ignore_errors = True)
        self.exists = []

    def makeExist(self, path):
        self.mutex.acquire()
        if not path in self.exists and not self.superSafeMode:
            os.makedirs(path)
        self.exists.append(path)
        self.mutex.release()

    def getProjRoot(self, proj):
        path = (self.root + os.sep + proj + os.sep)
        self.makeExist(path)
        return path

    def getDiffPath(self, proj, lang):
        path = (self.getProjRoot(proj) +
                lang + os.sep + "raw_diffs" + os.sep)
        self.makeExist(path)
        return path

    def getFilterOutputPath(self, proj, lang):
        path = (self.getProjRoot(proj) +
                lang + os.sep + "filter_output" + os.sep)
        self.makeExist(path)
        return path

    # is_new is true iff we're dealing with the new context
    def getCCFXInputPath(self, proj, lang, is_new):
        ext = '_old'
        if is_new:
            ext = '_new'
        path = (self.getProjRoot(proj) +
                lang + os.sep + "ccfx_input"  + ext + os.sep)
        self.makeExist(path)
        return path

    # is_new is true iff we're dealing with the new context
    def getLineMapPath(self, proj, lang, is_new):
        ext = '_old'
        if is_new:
            ext = '_new'
        path = (self.root + os.sep + proj + os.sep +
                lang + os.sep + "ccfx_mappings" + ext + os.sep)
        self.makeExist(path)
        return path

    def getCCFXOutputPath(self):
        path = self.root + os.sep + 'clones' + os.sep
        self.makeExist(path)
        return path

    def makeLineMapFileName(self, old_name):
        return old_name.partition('.')[0] + '.conv'

    def getCCXFPrepPath(self, proj, lang, is_new):
        return self.getCCFXInputPath(proj, lang, is_new) + '.ccfxprepdir' + os.sep

    def getCCFXOutputFileName(self, lang, is_new, is_tmp):
        if is_new:
            ext = '_new'
        else:
            ext = '_old'

        if is_tmp:
            ext = ext + '.ccfxd'
        else:
            ext = ext + '.txt'
        return lang + ext

    # the output of the ccfx prep scripts are a little funny,
    # find the ccfx prep file in path (a directory) for file name (no path)
    # ie self.findPrepFile('/home/user/myworkdir/more/.ccfxprepdir/', '0027.c')
    def findPrepFileFor(self, path, name):
        for f in os.listdir(path):
            if f.startswith(name):
                return f
        raise Exception(
                "Couldn't find prep file for diff with name: {0}".format(name))

    def getRepertoireOutputPath(self, lang, is_new):
        path = self.root + os.sep + 'repertoire' + os.sep
        self.makeExist(path)
        return path

    def getRepertoireOutputFileName(self, lang, is_new):
        return self.getCCFXOutputFileName(lang, is_new, False)

    def translateFilterToCCFXInput(self, filter_path):
        proj = PathBuilder.Proj0
        if not filter_path.startswith(self.getProjRoot(proj)):
            proj = PathBuilder.Proj1
        for lang in [LangDecider.CXX, LangDecider.JAVA, LangDecider.HXX]:
            filter_prefix = self.getFilterOutputPath(proj, lang)
            if filter_path.startswith(filter_prefix):
                break
        file_name = filter_path[len(filter_prefix):]
        return self.getCCFXInputPath(proj, lang) + file_name

    def getDBPathAndName(self):
        return self.root + os.sep + 'rep_db.pickle'

# figures out what language a file is
class LangDecider:
    NONE = 'none'
    CXX = 'cxx'
    JAVA = 'java'
    HXX = 'hxx'

    CXX_SUFF = '.' + CXX
    HXX_SUFF = '.' + HXX
    JAVA_SUFF = '.' + JAVA

    def __init__(self, c_suff, h_suff, j_suff):
        self.cSuff = c_suff
        self.hSuff = h_suff
        self.jSuff = j_suff
        self.filters = {
                'java' : DiffFilter(j_suff),
                'cxx'  : DiffFilter(c_suff),
                'hxx'  : DiffFilter(h_suff)
                }

    def getLang(self, path):
        if path.endswith(self.cSuff):
            return LangDecider.CXX
        if path.endswith(self.hSuff):
            return LangDecider.HXX
        if path.endswith(self.jSuff):
            return LangDecider.JAVA
        return LangDecider.NONE

    def isCode(self, path):
        if not path:
            return False
        if (path.endswith(self.cSuff) or
                path.endswith(self.hSuff) or
                path.endswith(self.jSuff)):
            return True
        return False

    def getSuffixFor(self, lang):
        if lang == LangDecider.CXX:
            return LangDecider.CXX_SUFF
        if lang == LangDecider.HXX:
            return LangDecider.HXX_SUFF
        if lang == LangDecider.JAVA:
            return LangDecider.JAVA_SUFF
        return '.none'

    def getSuffix(self):
        return (self.cSuff, self.hSuff, self.jSuff)


    def getFilter(self, lang):
        return self.filters[lang]
