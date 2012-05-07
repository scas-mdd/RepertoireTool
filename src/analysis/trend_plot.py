#!/usr/bin/env python
"""
Series of data are loaded from a .csv file, and their names are
displayed in a checkable list view. The user can select the series
it wants from the list and plot them on a matplotlib canvas.

Use the sample .csv file that comes with the script for an example
of data series.

Eli Bendersky (eliben@gmail.com)
License: this code is in the public domain
Last modified: 18.05.2009
"""
import sys, os, csv
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from pylab import *
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

class trendObj:
    def __init__(self,project_name=None,data=None,label=None):
        self.projName = project_name
        self.data = data
        self.label = label

    def __str__(self):
        print self.projName
        print self.data
        return self.projName

class trendPlot(object):
    def __init__(self):
        self.names = []
        self.data = {}
        self.label = {}

    def add_obj(self,trend_obj):
        self.names.append(trend_obj.projName)
        self.data[trend_obj.projName] = trend_obj.data
        self.label[trend_obj.projName] = trend_obj.label
        self.datalen = len(trend_obj.data)

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

class Form(QMainWindow):
    #plot_obj is of type trendPlot
    def __init__(self,plot_obj=None,parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle('PyQt & matplotlib demo: Data plotting')
#        self.filename = file_name
#        self.data = DataHolder()
        self.series_list_model = QStandardItemModel()

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.data = plot_obj
        self.load_data()
        self.update_ui()
        self.on_show()

    def load_data(self):
        self.fill_series_list(self.data.series_names())
#        self.status_text.setText("Loaded " + filename)
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
                self.axes.plot(range(len(series)), series, 'o-', label=name,picker=5)

        if has_series and self.legend_cb.isChecked():
            self.axes.legend()
        self.canvas.draw()

    def on_button_press(self,event):
        """ If the left mouse button is pressed: draw a little square.
        """
        print 'you pressed', event.key, event.xdata, event.ydata
        tb = get_current_fig_manager().toolbar
        x,y = event.xdata,event.ydata
        self.axes.plot([x],[y],'rs')
        self.canvas.draw()

        if event.button==1 and event.inaxes and tb.mode == '':
            x,y = event.xdata,event.ydata
            plot([x],[y],'rs')
            self.canvas.draw()


    def on_button_release(self,event):
        print 'you released', event.key, event.xdata, event.ydata

    def on_motion_notify(self,event):
        print 'you released', event.key, event.xdata, event.ydata

    def on_pick(self, event):
        print "on pick event"
        thisline = event.artist
        xdata, ydata = thisline.get_data()
        ind = event.ind
        print 'on pick line:', zip(xdata[ind], ydata[ind])
#        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on data with coords:\n %s" % zip(xdata[ind], ydata[ind])


        QMessageBox.information(self, "Click!", msg)

    def connect_events(self):
#        self.canvas.mpl_connect('pick_event', self.on_pick)
        gca().set_autoscale_on(False)
        self.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.canvas.mpl_connect('button_release_event', self.on_button_press)
#        self.cidmotion = self.canvas.mpl_connect('motion_notify_event', self.on_motion_notify)

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

        left_vbox = QVBoxLayout()
        left_vbox.addWidget(self.canvas)
        left_vbox.addWidget(self.mpl_toolbar)

        right_vbox = QVBoxLayout()
        right_vbox.addWidget(log_label)
        right_vbox.addWidget(self.series_list_view)
        right_vbox.addLayout(spins_hbox)
        right_vbox.addWidget(self.legend_cb)
        right_vbox.addWidget(self.show_button)
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
        self.file_menu = self.menuBar().addMenu("&File")

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
