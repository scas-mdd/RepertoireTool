#!/usr/bin/env python
"""
Shows extent of porting:
percentage of ported edits in each patch in each commit
License: this code is in the public domain
Last modified: 18.05.2009
"""
import sys, os, csv
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from pylab import *
import matplotlib.dates as dates
import matplotlib.ticker as ticker
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import *

import os
import pickle
from subprocess import Popen, PIPE


from rep_db import *

class trendPlot(object):
    #proj0, proj1 are map between commit_date and trendObj
    def __init__(self,proj0,proj1,rep_db):
        self.proj0 = proj0
        self.proj1 = proj1
        self.names = ['project 0','project 1']
        self.data = {}
        self.label = {}  #date
        self.label2 = {}  #date
        self.datalen = 0
        self.get_plot_data(rep_db)

    def get_plot_data(self,rep_db):
        if self.proj0 is None or self.proj1 is None:
            return None

        data = []
        label = []
        label2 = []

        for proj in (self.proj0,self.proj1):
            pcent_port = []
            x_label = []
            label_2 = []
            for cm_date,trnd_obj in sorted(proj.iteritems()):
                cm_id = trnd_obj.commitId
                total_edit = rep_db.getTotalEdit(cm_id)
                total_port = trnd_obj.metric
                pcent_edit = (float(total_port)/total_edit)*100
                pcent_port.append(pcent_edit)
                x_label.append(cm_date)
                label_2.append(trnd_obj.fileDist)
            data.append(pcent_port)
            label.append(x_label)
            label2.append(label_2)

        for i in (0,1):
            self.data[self.names[i]] = data[i]
            self.label[self.names[i]] = label[i]
            self.label2[self.names[i]] = label2[i]
            self.datalen += len(data[i])

        print data
    def series_names(self):
        """ Names of the data series
        """
        return self.names

    def series_len(self):
        """ Length of a data series
        """
        return self.datalen

    def series_count(self):
        return len(self.data)

    def get_series_data(self, name):
        return self.data[name]

    def get_series_label(self, name):
        return self.label[name]

    def get_file_dist(self, name):
        return self.label2[name]

class Form(QMainWindow):
    #plot_obj is of type trendPlot
    def __init__(self,plot_obj=None,parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle('Extent of Porting')
        self.series_list_model = QStandardItemModel()

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.data = plot_obj
        self.load_data()
        self.update_ui()
#        self.on_show()


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

    def on_show(self):
        self.axes.clear()
        self.axes.grid(True)

        has_series = False

        for row in range(self.series_list_model.rowCount()):
            model_index = self.series_list_model.index(row, 0)
            checked = self.series_list_model.data(model_index,
                Qt.CheckStateRole) == QVariant(Qt.Checked)
            name = str(self.series_list_model.data(model_index).toString())

            if checked:
                has_series = True
                x_from = self.from_spin.value()
                x_to = self.to_spin.value()
                series = self.data.get_series_data(name)[x_from:x_to + 1]
                label = self.data.get_series_label(name)[x_from:x_to + 1]
#                print label
                self.line, = self.axes.plot_date(label, series, 'o-', label=name,picker=5)
                setp(self.line, linewidth=3)
                self.axes.set_xlabel('commit dates')
                self.axes.set_ylabel('% of portes edits')
                ax = self.axes
                ax.xaxis.set_major_locator(dates.AutoDateLocator())
                ax.xaxis.set_minor_locator(dates.MonthLocator(interval=3))
#                ax.xaxis.set_minor_locator(dates.MonthLocator(bymonthday=30))

                ax.xaxis.set_major_formatter(ticker.NullFormatter())
                ax.xaxis.set_minor_formatter(dates.DateFormatter('%b %y'))
                for tick in ax.xaxis.get_minor_ticks():
                    tick.tick1line.set_markersize(0)
                    tick.tick2line.set_markersize(0)
                    tick.label1.set_horizontalalignment('center')
#                    tick.label1.set_rotation(25)
                    tick.label1.set_fontsize(8)

        if has_series and self.legend_cb.isChecked():
            self.axes.legend(loc='upper left')
        self.canvas.draw()
        self.bird_button.setVisible(True)


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
                file_list = self.data.get_file_dist(name)[x_from:x_to + 1]
                print "file_list:"
                print file_list

                #convert file_list to a hash
                proj_file_dist = {}
#                print series
                for dist in file_list:
                    print "dist:"
                    print dist
                    for k,v in dist.iteritems():
                        print "v:"
                        print v
                        if proj_file_dist.has_key(k) == 0:
                            proj_file_dist[k] = []
                        proj_file_dist[k].append(v[0])
                print proj_file_dist

                pickle.dump( proj_file_dist, open( "trend.pkl", "wn" ) )
                cmd_str = "./file_dist1.py " + "trend.pkl"
                os.system(cmd_str)
#                proc = Popen(cmd_str,shell=True,stdout=PIPE,stderr=PIPE)
                #need to spawn a process and call this function
#                import file_dist as fd
#                fd.gen_scatter_plot(proj_file_dist)


    def on_button_press(self,event):
        """ If the left mouse button is pressed: draw a little square.
        """
        if not event.inaxes: return
        print 'you pressed', event.key, event.xdata, event.ydata
        self.x_press = event.xdata
        self.y_press = event.ydata
        tb = get_current_fig_manager().toolbar

        if event.button==1 and event.inaxes and tb.mode == '':
            x,y = event.xdata,event.ydata
            plot([x],[y],'rs')
            self.canvas.draw()


    def on_button_release(self,event):
        if not event.inaxes: return
        print 'you released', event.key, event.xdata, event.ydata

    def on_pick(self, event):
        print "on pick event"
        if event.artist!= self.line: return True
        N = len(event.ind)
        if not N: return True
        thisline = event.artist
        xdata, ydata = thisline.get_data()
        ind = event.ind
        print 'on pick line:', zip(xdata[ind], ydata[ind])
        msg = "You've clicked on data with coords:\n %s" % zip(xdata[ind], ydata[ind])


        QMessageBox.information(self, "Click!", msg)

    def connect_events(self):
        self.canvas.mpl_connect('pick_event', self.on_pick)
#        gca().set_autoscale_on(False)
        self.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.canvas.mpl_connect('button_release_event', self.on_button_release)

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
        self.fig.suptitle('Extent of Porting', fontsize=15)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        self.axes = self.fig.add_subplot(111)

        self.connect_events()

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        log_label = QLabel("Data series:")
        self.series_list_view = QListView()
        self.series_list_view.setModel(self.series_list_model)

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

        self.show_button = QPushButton("&Show")
        self.connect(self.show_button, SIGNAL('clicked()'), self.on_show)

        self.bird_button = QPushButton("&Bird's Eye")
        self.connect(self.bird_button, SIGNAL('clicked()'), self.on_bird)
        self.bird_button.setVisible(False)

        left_vbox = QVBoxLayout()
        left_vbox.addWidget(self.canvas)
        left_vbox.addWidget(self.mpl_toolbar)

        right_vbox = QVBoxLayout()
        right_vbox.addWidget(log_label)
        right_vbox.addWidget(self.series_list_view)
        right_vbox.addLayout(spins_hbox)
        right_vbox.addWidget(self.legend_cb)
        right_vbox.addWidget(self.show_button)
        right_vbox.addWidget(self.bird_button)
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

#        load_action = self.create_action("&Load file",
#            shortcut="Ctrl+L", slot=self.load_file, tip="Load a file")
        quit_action = self.create_action("&Quit", slot=self.close,
            shortcut="Ctrl+Q", tip="Close the application")

#        self.add_actions(self.file_menu,
#            (load_action, None, quit_action))

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


def draw(trnd_plot):
    app = QApplication(['trend_plot.py'])
    print trnd_plot.names
    print trnd_plot.data[trnd_plot.names[0]]
    print trnd_plot.data[trnd_plot.names[1]]
    form = Form(trnd_plot)
    form.show()
    app.exec_()



# --------------------- test -----------------------#

def main():
    app = QApplication(sys.argv)
#   form = Form("/home/bray/Downloads/pyqt_dataplot_demo/qt_mpl_data.csv")
    form = Form("net_open.csv")
    form.show()
    app.exec_()


if __name__ == "__main__":
    print sys.argv
    main()
