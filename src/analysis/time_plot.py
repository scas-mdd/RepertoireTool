#!/usr/bin/env python
"""
Shows the delay to port a patch from one project to another

Last modified: 05.09.2012
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
from datetime import *

import os
from subprocess import Popen, PIPE


from rep_db import *

class timePlot(object):
    #proj0, proj1 are map between commit_date and trendObj
    def __init__(self,proj0,proj1):
        self.proj0 = proj0
        self.proj1 = proj1
        self.x = []
        self.y = []
        self.y_cum_list = []
        self.total_port = [sum(proj0.values()),sum(proj1.values())]

        self.names = ['project 0','project 1']
        self.x_data = {}
        self.y_data = {}
        self.y_cuml = {}
        self.datalen = 0

        self.set_plot_data()
        self.set_cuml_data()

        for i in (0,1):
            self.x_data[self.names[i]] = self.x[i]
            self.y_data[self.names[i]] = self.y[i]
            self.y_cuml[self.names[i]] = self.y_cum_list[i]
            self.datalen += len(self.x[i])

    def set_plot_data(self):
        if self.proj0 is None or self.proj1 is None:
            return None

        proj_num = 0
        for proj in (self.proj0,self.proj1):
            x = []
            y = []
            for days,port in sorted(proj.iteritems()):
                x.append(days)
                pcent_port = (float(port)*100)/self.total_port[proj_num]
                y.append(pcent_port)
            self.x.append(x)
            self.y.append(y)
            proj_num += 1

        print self.x
        print self.y


    def set_cuml_data(self):
        for i in range(len(self.y)):
            proj = self.y[i]
            cuml = 0
            cuml_proj = []
            for index in range(0,len(proj)):
                cuml += proj[index]
                cuml_proj.append(cuml)
            self.y_cum_list.append(cuml_proj)

    def series_names(self):
        """ Names of the data series
        """
        return self.names

    def series_len(self):
        """ Length of a data series
        """
        return self.datalen

    def series_count(self):
        return len(self.x_data)

    def get_series_data(self, name):
        return self.y_data[name]

    def get_cuml_data(self, name):
        return self.y_cuml[name]

    def get_series_label(self, name):
        return self.x_data[name]

class Form(QMainWindow):
    #plot_obj is of type trendPlot
    def __init__(self,plot_obj=None,parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle('Porting Latecy: How long it takes a patch to propagate')
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

    def on_show(self,isCuml=False):
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

                if isCuml is False:
                    series = self.data.get_series_data(name)[x_from:x_to + 1]
                else:
                    series = self.data.get_cuml_data(name)[x_from:x_to + 1]

                label = self.data.get_series_label(name)[x_from:x_to + 1]
                print series
                print label
#                print label
                self.line, = self.axes.plot(label, series, 'o-', label=name)
                self.axes.set_xlabel('number of days')
                self.axes.set_ylabel('% of ported edits')
                ax = self.axes

                for tick in ax.xaxis.get_minor_ticks():
                    tick.tick1line.set_markersize(0)
                    tick.tick2line.set_markersize(0)
                    tick.label1.set_horizontalalignment('center')
                    tick.label1.set_fontsize(8)

        if has_series and self.legend_cb.isChecked():
            if isCuml is True:
                self.axes.legend(loc=4)
            else:
                self.axes.legend(loc='upper center')
        self.canvas.draw()
        self.cuml_button.setVisible(True)


    def on_cuml(self):
        print "pressed cuml's button"
        self.on_show(True)


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
        QMessageBox.about(self, "Porting Latency", msg.strip())

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
        self.fig.suptitle('Porting Latency', fontsize=15)
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

        self.show_button = QPushButton("Porting &Latency")
        self.connect(self.show_button, SIGNAL('clicked()'), self.on_show)

        self.cuml_button = QPushButton("Cumulative Distribution")
        self.connect(self.cuml_button, SIGNAL('clicked()'), self.on_cuml)
        self.cuml_button.setVisible(True)

        left_vbox = QVBoxLayout()
        left_vbox.addWidget(self.canvas)
        left_vbox.addWidget(self.mpl_toolbar)

        right_vbox = QVBoxLayout()
        right_vbox.addWidget(log_label)
        right_vbox.addWidget(self.series_list_view)
        right_vbox.addLayout(spins_hbox)
        right_vbox.addWidget(self.legend_cb)
        right_vbox.addWidget(self.show_button)
        right_vbox.addWidget(self.cuml_button)
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
            tip='About Porting Latency')

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


def draw(time_plot):
    app = QApplication(['time_plot.py'])
    print time_plot.names
    print time_plot.x_data[time_plot.names[0]]
    print time_plot.y_data[time_plot.names[0]]
    print time_plot.x_data[time_plot.names[1]]
    print time_plot.y_data[time_plot.names[1]]
    form = Form(time_plot)
    form.show()
    app.exec_()



# --------------------- test -----------------------#
#should be called from time_dist.py
