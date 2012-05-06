# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/analysis.ui'
#
# Created: Sun May  6 15:46:49 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RepWizard(object):
    def setupUi(self, RepWizard):
        RepWizard.setObjectName(_fromUtf8("RepWizard"))
        RepWizard.resize(499, 352)
        RepWizard.setWindowTitle(QtGui.QApplication.translate("RepWizard", "Repertoire Tool Kit", None, QtGui.QApplication.UnicodeUTF8))
        self.page0 = QtGui.QWizardPage()
        self.page0.setObjectName(_fromUtf8("page0"))
        self.welcomeLabel = QtGui.QLabel(self.page0)
        self.welcomeLabel.setGeometry(QtCore.QRect(10, 10, 321, 16))
        self.welcomeLabel.setText(QtGui.QApplication.translate("RepWizard", "Welcome to the Repertoire analysis Tool Kit!", None, QtGui.QApplication.UnicodeUTF8))
        self.welcomeLabel.setObjectName(_fromUtf8("welcomeLabel"))
        self.repDBLine = QtGui.QLineEdit(self.page0)
        self.repDBLine.setGeometry(QtCore.QRect(10, 90, 341, 31))
        self.repDBLine.setText(_fromUtf8(""))
        self.repDBLine.setObjectName(_fromUtf8("repDBLine"))
        self.repDBLabel = QtGui.QLabel(self.page0)
        self.repDBLabel.setGeometry(QtCore.QRect(10, 60, 151, 31))
        self.repDBLabel.setText(QtGui.QApplication.translate("RepWizard", "Repertoire Database:", None, QtGui.QApplication.UnicodeUTF8))
        self.repDBLabel.setObjectName(_fromUtf8("repDBLabel"))
        self.repDBbrowseButton = QtGui.QPushButton(self.page0)
        self.repDBbrowseButton.setGeometry(QtCore.QRect(360, 90, 97, 27))
        self.repDBbrowseButton.setText(QtGui.QApplication.translate("RepWizard", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.repDBbrowseButton.setObjectName(_fromUtf8("repDBbrowseButton"))
        self.line = QtGui.QFrame(self.page0)
        self.line.setGeometry(QtCore.QRect(10, 30, 461, 20))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.timeLabel = QtGui.QLabel(self.page0)
        self.timeLabel.setGeometry(QtCore.QRect(10, 140, 321, 31))
        self.timeLabel.setText(QtGui.QApplication.translate("RepWizard", "Please Select a time frame to analyze data:", None, QtGui.QApplication.UnicodeUTF8))
        self.timeLabel.setObjectName(_fromUtf8("timeLabel"))
        self.errorLabel0 = QtGui.QLabel(self.page0)
        self.errorLabel0.setGeometry(QtCore.QRect(10, 260, 341, 17))
        self.errorLabel0.setAutoFillBackground(False)
        self.errorLabel0.setText(QtGui.QApplication.translate("RepWizard", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#ff0000;\">Please select two valid directories.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.errorLabel0.setObjectName(_fromUtf8("errorLabel0"))
        self.startLabel = QtGui.QLabel(self.page0)
        self.startLabel.setGeometry(QtCore.QRect(10, 170, 131, 31))
        self.startLabel.setText(QtGui.QApplication.translate("RepWizard", "start date:", None, QtGui.QApplication.UnicodeUTF8))
        self.startLabel.setObjectName(_fromUtf8("startLabel"))
        self.endLabel = QtGui.QLabel(self.page0)
        self.endLabel.setGeometry(QtCore.QRect(10, 210, 131, 31))
        self.endLabel.setText(QtGui.QApplication.translate("RepWizard", "end date:", None, QtGui.QApplication.UnicodeUTF8))
        self.endLabel.setObjectName(_fromUtf8("endLabel"))
        self.startComboBox = QtGui.QComboBox(self.page0)
        self.startComboBox.setGeometry(QtCore.QRect(110, 180, 161, 27))
        self.startComboBox.setObjectName(_fromUtf8("startComboBox"))
        self.endComboBox = QtGui.QComboBox(self.page0)
        self.endComboBox.setGeometry(QtCore.QRect(110, 220, 161, 27))
        self.endComboBox.setObjectName(_fromUtf8("endComboBox"))
        RepWizard.addPage(self.page0)
        self.wizardPage = QtGui.QWizardPage()
        self.wizardPage.setObjectName(_fromUtf8("wizardPage"))
        self.fileButton = QtGui.QPushButton(self.wizardPage)
        self.fileButton.setGeometry(QtCore.QRect(240, 110, 217, 27))
        self.fileButton.setText(QtGui.QApplication.translate("RepWizard", "File Distribution", None, QtGui.QApplication.UnicodeUTF8))
        self.fileButton.setObjectName(_fromUtf8("fileButton"))
        self.trendButton = QtGui.QPushButton(self.wizardPage)
        self.trendButton.setGeometry(QtCore.QRect(240, 60, 217, 27))
        self.trendButton.setText(QtGui.QApplication.translate("RepWizard", "Trend", None, QtGui.QApplication.UnicodeUTF8))
        self.trendButton.setObjectName(_fromUtf8("trendButton"))
        self.devButton = QtGui.QPushButton(self.wizardPage)
        self.devButton.setGeometry(QtCore.QRect(240, 170, 217, 27))
        self.devButton.setText(QtGui.QApplication.translate("RepWizard", "developer\'s activity", None, QtGui.QApplication.UnicodeUTF8))
        self.devButton.setObjectName(_fromUtf8("devButton"))
        self.trendLabel = QtGui.QLabel(self.wizardPage)
        self.trendLabel.setGeometry(QtCore.QRect(10, 60, 161, 27))
        self.trendLabel.setText(QtGui.QApplication.translate("RepWizard", "Porting Trend", None, QtGui.QApplication.UnicodeUTF8))
        self.trendLabel.setObjectName(_fromUtf8("trendLabel"))
        self.fileLabel = QtGui.QLabel(self.wizardPage)
        self.fileLabel.setGeometry(QtCore.QRect(10, 110, 171, 27))
        self.fileLabel.setText(QtGui.QApplication.translate("RepWizard", "File Distribution", None, QtGui.QApplication.UnicodeUTF8))
        self.fileLabel.setObjectName(_fromUtf8("fileLabel"))
        self.devLabel = QtGui.QLabel(self.wizardPage)
        self.devLabel.setGeometry(QtCore.QRect(10, 170, 181, 27))
        self.devLabel.setText(QtGui.QApplication.translate("RepWizard", "Developer\'s Distribution", None, QtGui.QApplication.UnicodeUTF8))
        self.devLabel.setObjectName(_fromUtf8("devLabel"))
        self.timeLabel_2 = QtGui.QLabel(self.wizardPage)
        self.timeLabel_2.setGeometry(QtCore.QRect(10, 230, 181, 27))
        self.timeLabel_2.setText(QtGui.QApplication.translate("RepWizard", "Timing Analysis", None, QtGui.QApplication.UnicodeUTF8))
        self.timeLabel_2.setObjectName(_fromUtf8("timeLabel_2"))
        self.timeButton = QtGui.QPushButton(self.wizardPage)
        self.timeButton.setGeometry(QtCore.QRect(240, 230, 217, 27))
        self.timeButton.setText(QtGui.QApplication.translate("RepWizard", "timing analysis", None, QtGui.QApplication.UnicodeUTF8))
        self.timeButton.setObjectName(_fromUtf8("timeButton"))
        self.welcomeLabel_2 = QtGui.QLabel(self.wizardPage)
        self.welcomeLabel_2.setGeometry(QtCore.QRect(10, 10, 321, 16))
        self.welcomeLabel_2.setText(QtGui.QApplication.translate("RepWizard", "Repertoire analysis Tool Kit!", None, QtGui.QApplication.UnicodeUTF8))
        self.welcomeLabel_2.setObjectName(_fromUtf8("welcomeLabel_2"))
        self.line_2 = QtGui.QFrame(self.wizardPage)
        self.line_2.setGeometry(QtCore.QRect(0, 30, 461, 20))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        RepWizard.addPage(self.wizardPage)

        self.retranslateUi(RepWizard)
        QtCore.QMetaObject.connectSlotsByName(RepWizard)

    def retranslateUi(self, RepWizard):
        pass

