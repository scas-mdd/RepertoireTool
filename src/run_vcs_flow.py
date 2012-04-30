#!/usr/bin/env python
import sys
from datetime import datetime

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QWizardPage, QWizard, QApplication
from PyQt4.QtCore import Qt, QDate, QThread, QObject
from ui.page_projdir import Ui_ProjDirPage
from ui.page_confirm import Ui_ConfirmPage
from ui.page_ccfx import Ui_CcfxPage
from ui.page_vcs_suffix import Ui_VcsSuffixPage
from ui.page_vcs_when import Ui_VcsWhenPage
from ui.page_vcs_where import Ui_VcsWherePage
from ui.page_vcs_which import Ui_VcsWhichPage
from ui.page_welcome import Ui_WelcomePage
from ui.page_working import Ui_WorkingPage
from ui.page_final import Ui_FinalPage

from simple_model import SimpleModel
from simple_driver import SimpleDriver
from path_builder import PathBuilder
from vcs_types import VcsTypes

def pick_path(edit_line, msg, is_dir=True):
    if is_dir:
        path = QtGui.QFileDialog.getExistingDirectory(None, msg)
    else:
        path = QtGui.QFileDialog.getOpenFileName(None, msg)
    if path:
        edit_line.setText(path)

class WelcomePage(QWizardPage):
    def __init__(self, model, ui, parent=None):
        QWizardPage.__init__(self, parent)
        self.ui = ui
        self.model = model

    def postSetup(self):
        pass

    def validatePage(self):
        if self.ui.newProjBtn.isChecked():
            return True
        return False

class ProjDirPage(QWizardPage):
    def __init__(self, model, ui, parent=None):
        QWizardPage.__init__(self, parent)
        self.ui = ui
        self.model = model

    def initializePage(self):
        self.ui.projDirLine.setText(self.model.getProjDir())

    def postSetup(self):
        self.ui.errorLabel_projDir.setVisible(False)
        self.ui.projDirBtn.clicked.connect(lambda : pick_path(
            self.ui.projDirLine, 'Select project directory'))

    def validatePage(self):
        path = str(self.ui.projDirLine.text())
        if not self.model.setProjDir(path):
            # show an informative message here
            self.ui.errorLabel_projDir.setVisible(True)
            return False
        self.ui.errorLabel_projDir.setVisible(False)
        return True

class CcfxPage(QWizardPage):
    def __init__(self, model, ui, parent=None):
        QWizardPage.__init__(self, parent)
        self.ui = ui
        self.model = model

    def initializePage(self):
        self.ui.ccfxPathLine.setText(self.model.getCcfxPath())

    def postSetup(self):
        self.ui.errorLabel_ccfx.setVisible(False)
        self.ui.ccfxPathBtn.clicked.connect(lambda : pick_path(
            self.ui.ccfxPathLine, 'Select ccfx binary', False))

    def validatePage(self):
        path = str(self.ui.ccfxPathLine.text())
        if not self.model.setCcfxPath(path):
            self.ui.errorLabel_ccfx.setVisible(True)
            return False
        self.ui.errorLabel_ccfx.setVisible(False)
        self.model.setCcfxTokenSize(str(self.ui.ccfxTokenCombo.currentText()))
        return True

class VcsSuffixPage(QWizardPage):
    def __init__(self, proj, model, ui, parent=None):
        QWizardPage.__init__(self, parent)
        self.proj = proj
        self.ui = ui
        self.model = model
        self.proj = proj

    def initializePage(self):
        c_suff, h_suff, j_suff = self.model.getVcsSuffix(self.proj)
        self.ui.cSuffLine.setText(c_suff)
        self.ui.hSuffLine.setText(h_suff)
        self.ui.jSuffLine.setText(j_suff)

    def postSetup(self):
        pass

    def validatePage(self):
        c_suff = str(self.ui.cSuffLine.text())
        h_suff = str(self.ui.hSuffLine.text())
        j_suff = str(self.ui.jSuffLine.text())
        return self.model.setVcsSuffix(self.proj, c_suff, h_suff, j_suff)

class VcsWhenPage(QWizardPage):
    def __init__(self, proj, model, ui, parent=None):
        QWizardPage.__init__(self, parent)
        self.proj = proj
        self.ui = ui
        self.model = model

    def postSetup(self):
        self.ui.vcsWhenEnd.setDate(QDate.currentDate())

    def initializePage(self):
        start, end = self.model.getVcsTimeWindow(self.proj)
        if not start or not end:
            return
        date_start = QDate(start.year, start.month, start.day)
        date_end = QDate(end.year, end.month, end.day)
        self.ui.vcsWhenStart.setDate(date_start)
        self.ui.vcsWhenEnd.setDate(date_end)

    def validatePage(self):
        sdate = self.ui.vcsWhenStart.date()
        edate = self.ui.vcsWhenEnd.date()
        start = datetime(
                year = int(sdate.year()),
                month = int(sdate.month()),
                day = int(sdate.day()))
        end = datetime(
                year = int(edate.year()),
                month = int(edate.month()),
                day = int(edate.day()))
        return self.model.setVcsWhen(self.proj, start, end)

class VcsWherePage(QWizardPage):
    def __init__(self, proj, model, ui, parent=None):
        QWizardPage.__init__(self, parent)
        self.proj = proj
        self.ui = ui
        self.model = model

    def postSetup(self):
        self.ui.errorLabel_vcsWhere.setVisible(False)
        self.ui.vcsDirSelBtn.clicked.connect(lambda : pick_path(
            self.ui.vcsDirLine, 'Select repository root'))

    def initializePage(self):
        self.ui.vcsDirLine.setText(self.model.getVcsWhere(self.proj))

    def validatePage(self):
        path = str(self.ui.vcsDirLine.text())
        return self.model.setVcsWhere(self.proj, path)

class VcsWhichPage(QWizardPage):
    def __init__(self, proj, model, ui, parent=None):
        QWizardPage.__init__(self, parent)
        self.proj = proj
        self.ui = ui
        self.model = model

    def postSetup(self):
        if self.proj == PathBuilder.Proj0:
            self.ui.vcsSelectFirst.setVisible(True)
            self.ui.vcsSelectSecond.setVisible(False)
        else:
            self.ui.vcsSelectFirst.setVisible(False)
            self.ui.vcsSelectSecond.setVisible(True)

    def initializePage(self):
        which = self.model.getVcsWhich(self.proj)
        if not which:
            return
        if which == VcsTypes.Git:
            self.ui.vcsGitBtn.setChecked(True)
        elif which == VcsTypes.Hg:
            self.ui.vcsHgBtn.setChecked(True)
        elif which == VcsTypes.Svn:
            self.ui.vcsSvnBtn.setChecked(True)

    def validatePage(self):
        if self.ui.vcsGitBtn.isChecked():
            return self.model.setVcsWhich(self.proj, VcsTypes.Git)
        elif self.ui.vcsHgBtn.isChecked():
            return self.model.setVcsWhich(self.proj, VcsTypes.Hg)
        elif self.ui.vcsSvnBtn.isChecked():
            return self.model.setVcsWhich(self.proj, VcsTypes.Svn)
        return False

class ConfirmPage(QWizardPage):
    def __init__(self, model, ui, parent=None):
        QWizardPage.__init__(self, parent)
        self.ui = ui
        self.model = model

    def postSetup(self):
        pass

    def initializePage(self):
        self.ui.errorLabel_confirm.setVisible(False)

    def validatePage(self):
        if self.model.isComplete():
            return True
        self.ui.errorLabel_confirm.setVisible(True)
        return False

class WorkingPage(QWizardPage):
    def __init__(self, model, ui, parent=None):
        QWizardPage.__init__(self, parent)
        self.ui = ui
        self.model = model
        # this one is a little difference since it has background work logic
        self.workerThread = QThread()
        self.workerThread.start()
        self.driver = SimpleDriver()
        self.driver.moveToThread(self.workerThread)
        self.isDone = False
        QObject.connect(
                self,
                QtCore.SIGNAL("startProcessing"),
                self.driver.process,
                Qt.QueuedConnection)
        QObject.connect(
                self.driver,
                QtCore.SIGNAL("progress"),
                self.updateProgress,
                Qt.QueuedConnection)
        QObject.connect(
                self.driver,
                QtCore.SIGNAL("done"),
                self.workerDone,
                Qt.QueuedConnection)

    def workerDone(self, args):
        msg, finished_successfully = args
        print 'worker finished: ' + str(finished_successfully) + ' ' + msg
        if finished_successfully:
            self.isDone = True
            self.ui.progressBar.setValue(100)
            self.ui.workingLabel.setText(msg)
        else:
            self.isDone = False
            msgBox = QtGui.QMessageBox(self)
            msgBox.setText(msg)
            msgBox.exec_()

    def updateProgress(self, args):
        msg, frac = args
        self.ui.progressBar.setValue(int(frac * 100))
        self.ui.workingLabel.setText(msg)

    def postSetup(self):
        pass

    def initializePage(self):
        self.isDone = False
        self.ui.workingLabel.setText('')
        self.ui.progressBar.setValue(0)
        print 'worker starting'
        self.driver.startWorking(lambda :
                self.emit(QtCore.SIGNAL("startProcessing"), self.model))

    def validatePage(self):
        return self.isDone

    # called when the use hits back
    def cleanupPage(self):
        print 'cleaning up '
        # this blocks until the driver stops, but is thread safe
        self.driver.stopWorking()

class FinalPage(QWizardPage):
    def __init__(self, model, ui, parent=None):
        QWizardPage.__init__(self, parent)
        self.ui = ui
        self.model = model

    def postSetup(self):
        pass

    def validatePage(self):
        return True

class VcsWizard(QWizard):
    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.model = SimpleModel()

        ui = Ui_WelcomePage()
        realPage = WelcomePage(self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_ProjDirPage()
        realPage = ProjDirPage(self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_CcfxPage()
        realPage = CcfxPage(self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_VcsWhichPage()
        realPage = VcsWhichPage(PathBuilder.Proj0, self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_VcsWherePage()
        realPage = VcsWherePage(PathBuilder.Proj0, self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_VcsWhenPage()
        realPage = VcsWhenPage(PathBuilder.Proj0, self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_VcsSuffixPage()
        realPage = VcsSuffixPage(PathBuilder.Proj0, self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_VcsWhichPage()
        realPage = VcsWhichPage(PathBuilder.Proj1, self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_VcsWherePage()
        realPage = VcsWherePage(PathBuilder.Proj1, self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_VcsWhenPage()
        realPage = VcsWhenPage(PathBuilder.Proj1, self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_VcsSuffixPage()
        realPage = VcsSuffixPage(PathBuilder.Proj1, self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_ConfirmPage()
        realPage = ConfirmPage(self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_WorkingPage()
        realPage = WorkingPage(self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

        ui = Ui_FinalPage()
        realPage = FinalPage(self.model, ui, self)
        ui.setupUi(realPage)
        ui.retranslateUi(realPage)
        realPage.postSetup()
        self.addPage(realPage)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    v = VcsWizard()
    if len(sys.argv) > 1 and 'wileytest' == sys.argv[1]:
        v.model.setProjDir('/home/wiley/ws/RepertoireTool/src')
        v.model.setCcfxPath('/home/wiley/ws/ccfxfiles/ubuntu32/ccfx')
        v.model.setCcfxTokenSize(40)
        v.model.setVcsWhich(PathBuilder.Proj0, VcsTypes.Hg)
        v.model.setVcsWhen(PathBuilder.Proj0, datetime(2012, 1, 20), datetime(2012, 3, 20))
        v.model.setVcsWhere(PathBuilder.Proj0, '/home/wiley/ws/opensource/xemacs')
        v.model.setVcsSuffix(PathBuilder.Proj0, '.c', '.h', '.java')
        v.model.setVcsWhich(PathBuilder.Proj1, VcsTypes.Git)
        v.model.setVcsWhere(PathBuilder.Proj1, '/home/wiley/ws/opensource/emacs')
        v.model.setVcsWhen(PathBuilder.Proj1, datetime(2012, 1, 20), datetime(2012, 3, 20))
        v.model.setVcsSuffix(PathBuilder.Proj1, '.c', '.h', '.java')
    v.show()
    sys.exit(app.exec_())

