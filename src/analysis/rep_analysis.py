#!/usr/bin/env python
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QThread, QObject
from ui.analysis import Ui_RepWizard

import os
from subprocess import Popen, PIPE
import trend

class RepWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_RepWizard()
        self.ui.setupUi(self)
        self.postSetup()
        self.processingDone = False
        self.rep_db = None

    def postSetup(self):
        self.page(0).validatePage = self.validatePage0
        self.page(1).validatePage = self.validatePage1

        self.ui.repDBbrowseButton.clicked.connect(lambda : self.pickFile(
            self.ui.repDBLine, 'Select repertoire Database'))

        self.ui.trendButton.clicked.connect(lambda : self.showTrend())
        self.ui.fileButton.clicked.connect(lambda : self.showFileDist())
        self.ui.devButton.clicked.connect(lambda : self.showDevDist())
        self.ui.timeButton.clicked.connect(lambda : self.showTimeDist())

        self.ui.errorLabel0.setVisible(False)

    def pickFile(self, line, msg):
        path = QtGui.QFileDialog.getOpenFileName(self, msg)
        if path:
            line.setText(path)
            self.rep_db = path
        else: self.ui.errorLabel0.setVisible(True)

    def showTrend(self):
        print "showTrend"
        cmd_str = "./trend.py " + str(self.rep_db)
        proc = Popen(cmd_str,shell=True,stdout=PIPE,stderr=PIPE)
#        os.system(cmd_str)


    def showFileDist(self):
        print "showFileDist"
        cmd_str = "./file_dist.py " + str(self.rep_db)
        proc = Popen(cmd_str,shell=True,stdout=PIPE,stderr=PIPE)
#        os.system(cmd_str)

    def showDevDist(self):
        print "showDevDist"
        cmd_str = "./dev_dist.py " + str(self.rep_db)
        proc = Popen(cmd_str,shell=True,stdout=PIPE,stderr=PIPE)
#        os.system(cmd_str)

    def showTimeDist(self):
        print "showTimeDist"
        cmd_str = "./time_dist.py " + str(self.rep_db)
        proc = Popen(cmd_str,shell=True,stdout=PIPE,stderr=PIPE)
#        os.system(cmd_str)

    def validatePage0(self):
        return True

    def validatePage1(self):
        return True

    def setTestValues(self, rep_db_path):
        print rep_db_path
        self.rep_db = rep_db_path
        self.ui.repDBLine.setText(rep_db_path)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = RepWizard()
    if len(sys.argv) > 1 and 'braytest' == sys.argv[1]:
        myapp.setTestValues('/home/bray/RepertoireTool/src/analysis/pckl.p')
    myapp.show()
    sys.exit(app.exec_())

