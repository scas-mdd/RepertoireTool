#!/usr/bin/env python
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QThread, QObject
from ui.analysis import Ui_RepWizard


class RepWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_RepWizard()
        self.ui.setupUi(self)
        self.postSetup()
        self.processingDone = False

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
        else: self.ui.errorLabel0.setVisible(True)

    def showTrend(self):
        print "showTrend"

    def showFileDist(self):
        print "showFileDist"

    def showDevDist(self):
        print "showDevDist"

    def showTimeDist(self):
        print "showTimeDist"

    def validatePage0(self):
        return True

    def validatePage1(self):
        return True

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = RepWizard()
    myapp.show()
    sys.exit(app.exec_())

