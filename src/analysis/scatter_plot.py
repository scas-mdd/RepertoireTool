#!/usr/bin/env python
"""
A scattered diagram of files where porting is done
License: this code is in the public domain
Last modified: 05.09.2010
"""
import sys, os, csv
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from pylab import *
import matplotlib.dates as dates
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from datetime import *

import os
from subprocess import Popen, PIPE

class graphObj:
    def __init__(self):
        self.data = []
        self.label = []
        self.indx2label = {} #map between data index and label

class scatterPlot:
    def __init__(self):
        self.x = graphObj()
        self.y = graphObj()
        self.color_map = [] #for different values we'll color the map differently
        self.set_value("","",0) #initialize the 1st value

    def series_len(self):
        return len(self.x.data)

    def series_count(self):
        return len(self.x.data)

    def set_value(self,x_val,y_val,value):

        if self.x.indx2label.has_key(x_val) == 0:
            self.x.indx2label[x_val] = len(self.x.label)
            self.x.label.append(x_val)

        if self.y.indx2label.has_key(y_val) == 0:
            self.y.indx2label[y_val] = len(self.y.label)
            self.y.label.append(y_val)

        if value >= 1:
            self.x.data.append(self.x.indx2label[x_val])
            self.y.data.append(self.y.indx2label[y_val])
            self.color_map.append(value)

    def set_file_hash(self,file_hash):
        """
        this is of the form
        file_hash[(file1:file2)] = {start1-end1\tstart2-end2\tmetric}
        """
        self.fileHash = file_hash

class Form(QMainWindow):
    #plot_obj is of type scatterPlot
    def __init__(self,plot_obj=None,parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle('File Distribution')
        self.series_list_model = QStandardItemModel()

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.data = plot_obj
        self.update_ui()
        self.on_show()

    def load_data(self):
        self.fill_series_list(self.data.series_names())
        self.update_ui()

    def update_ui(self):
        if self.data.series_count() > 0 and self.data.series_len() > 0:
            self.from_spin.setValue(0)
            self.to_spin.setValue(self.data.series_len() - 1)

            for w in [self.from_spin, self.to_spin]:
                w.setRange(0, self.data.series_len() - 1)
                w.setEnabled(True)
        else:
            for w in [self.from_spin, self.to_spin]:
                w.setEnabled(False)

    def get_ticker(x,pos):
        return self.data.x.label[pos]

    def on_show(self,isLabel=False):
        self.axes.clear()
        self.axes.grid(True)

        has_series = False

        x_from = self.from_spin.value()
        x_to = self.to_spin.value()
        x_data = self.data.x.data
        y_data = self.data.y.data
        x_label = self.data.x.label
        y_label = self.data.y.label
        color_map = self.data.color_map
        self.axes.scatter(x_data,y_data,c=color_map,s=30,marker='o',picker=5)

        if isLabel is False:
            self.axes.xaxis.set_major_formatter(ticker.NullFormatter())
            self.axes.yaxis.set_major_formatter(ticker.NullFormatter())
        else:
            self.axes.set_xticklabels(x_label, rotation=0)
            self.axes.set_yticklabels(y_label, rotation=0)

        self.axes.xaxis.set_label_text("files from project 0")
        self.axes.yaxis.set_label_text("files from project 1")
        self.axes.yaxis.set_label_position('right')

        self.canvas.draw()



    def on_bird(self):
        print "pressed bird's button"

        for row in range(self.series_list_model.rowCount()):
            model_index = self.series_list_model.index(row, 0)
            checked = self.series_list_model.data(model_index,
                Qt.CheckStateRole) == QVariant(Qt.Checked)
            name = str(self.series_list_model.data(model_index).toString())

            if checked:
                x_from = self.from_spin.value()
                x_to = self.to_spin.value()
                series = self.data.get_series_data(name)[x_from:x_to + 1]
                file_dist = self.data.get_file_dist(name)[x_from:x_to + 1]
                proj_file_dist = {}
                print file_dist
#                print series
                for dist in file_dist:
                    print dist
                    for k,v in dist.iteritems():
                        if proj_file_dist.has_key(k) == 0:
                            proj_file_dist[k] = 0
                        proj_file_dist[k] += int(v)
                print proj_file_dist
                #need to spawn a process and call this function
                import file_dist as fd
                fd.gen_scatter_plot(proj_file_dist)

    def on_label(self):
        print "pressed label button"
        self.on_show(True)

    def on_display(self):
        print "pressed file button"
#        self.file_button.setVisible(False)
#        self.log_label1.setText("")
        print "selected files: proj0:%s , proj1:%s\n" % (self.file1,self.file2)
        clones = self.data.fileHash.get((self.file1,self.file2),None)
        print clones
        for clone in clones:
            cl1,cl2,metric = clone.split("\t")
            fname1,cl1 = cl1.split(":")
            start1,end1 = cl1.split("-")
            fname2,cl2 = cl2.split(":")
            start2,end2 = cl2.split("-")
            clone1 = fname1 + ":" + start1 + ":" + end1
            clone2 = fname2 + ":" + start2 + ":" + end2
            args = "./display_diff.py " + clone1 + " " + clone2
            print args
            os.system(args)

#---------------event handling routines--------#

    def on_button_press(self,event):
        """ If the left mouse button is pressed: draw a little square.
        """
        if not event.inaxes: return
        print 'you pressed', event.key, event.xdata, event.ydata
        x_press = round(event.xdata)
        y_press = round(event.ydata)
#        QMessageBox.information(self,"Click!", msg)
        x_label = self.data.x.label
        y_label = self.data.y.label
        self.file1 = x_label[int(x_press)]
        self.file2 = y_label[int(y_press)]
        msg = "selected files: proj0:%s , proj1:%s\n" % (self.file1,self.file2)
        self.log_label1.setText(msg)
        self.file_button.setVisible(True)


    def connect_events(self):
        self.canvas.mpl_connect('button_press_event', self.on_button_press)

    def on_about(self):
        msg = __doc__
        QMessageBox.about(self, "About the demo", msg.strip())

    def fill_series_list(self, names):
        self.series_list_model.clear()

        for name in names:
            item = QStandardItem(name)
            item.setCheckState(Qt.Unchecked)
            item.setCheckable(True)
            self.series_list_model.appendRow(item)

    def create_main_frame(self):
        self.main_frame = QWidget()

        plot_frame = QWidget()

        self.dpi = 100
        self.fig = Figure((6.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        self.axes = self.fig.add_subplot(111)

        self.connect_events()

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        log_label = QLabel("\nTo browse ported code,\n Please select  a data point\n ")
        self.series_list_view = QListView()
        self.series_list_view.setModel(self.series_list_model)

        self.log_label1 = QLabel("")

        spin_label1 = QLabel('X from')
        self.from_spin = QSpinBox()
        spin_label2 = QLabel('to')
        self.to_spin = QSpinBox()

        spins_hbox = QHBoxLayout()
        spins_hbox.addWidget(spin_label1)
        spins_hbox.addWidget(self.from_spin)
        spins_hbox.addWidget(spin_label2)
        spins_hbox.addWidget(self.to_spin)
        spins_hbox.addStretch(1)

        self.legend_cb = QCheckBox("Show L&egend")
        self.legend_cb.setChecked(False)

        self.label_button = QPushButton("&Display Label")
        self.connect(self.label_button, SIGNAL('clicked()'), self.on_label)
        self.label_button.setVisible(True)

        self.file_button = QPushButton("&Display Portings")
        self.connect(self.file_button, SIGNAL('clicked()'), self.on_display)
        self.file_button.setVisible(False)

        left_vbox = QVBoxLayout()
        left_vbox.addWidget(self.canvas)
        left_vbox.addWidget(self.mpl_toolbar)
        left_vbox.addWidget(self.log_label1)

        right_vbox = QVBoxLayout()
        right_vbox.addWidget(self.label_button)
        right_vbox.addWidget(log_label)
        right_vbox.addWidget(self.file_button)
        right_vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addLayout(left_vbox)
        hbox.addLayout(right_vbox)
        self.main_frame.setLayout(hbox)

        self.setCentralWidget(self.main_frame)

    def create_status_bar(self):
        self.status_text = QLabel("Extent of porting")
        self.statusBar().addWidget(self.status_text, 1)

    def create_menu(self):
#        self.file_menu = self.menuBar().addMenu("&File")

        quit_action = self.create_action("&Quit", slot=self.close,
            shortcut="Ctrl+Q", tip="Close the application")

        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About",
            shortcut='F1', slot=self.on_about,
            tip='About the demo')

        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None,
                        icon=None, tip=None, checkable=False,
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


def draw(scatter_plot):
    app = QApplication(['scatter_plot.py'])
    form = Form(scatter_plot)
    form.show()
    app.exec_()



# --------------------- test -----------------------#

if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_map = {('file1', 'File1'): 1, ('file1', 'File3'): 3,
            ('file2', 'File2'): 1,
            ('file3', 'File1'): 5, ('file3', 'File2'): 4, ('file3', 'File3'): 2
           }
    myPlot = scatterPlot()

    for key, value in sorted(file_map.iteritems(), key=lambda (k,v): (v,k)):
        file1,file2 = key
#        print file1,file2
#        print value
        myPlot.set_value(file1,file2,value)

    form = Form(myPlot)
    form.show()
    app.exec_()

