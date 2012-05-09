#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt

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


    def draw(self,figSize=10,markerSize=50):
        X = self.x.data
        Y = self.y.data

        fig = plt.figure(1, figsize=(figSize,figSize))
        fig.suptitle('A Bird\'s eye view', fontsize=12)

#        self.connect_events()

        plt.scatter(X,Y,c=self.color_map,s=markerSize,marker='o',picker='5')
        plt.xticks(range(len(X)),self.x.label,size='small')
        plt.yticks(range(len(Y)),self.y.label,size='small')
        plt.xlim(-1,len(self.x.label))
        plt.ylim(-1,len(self.y.label))
        plt.xlabel( "Files from project0" )
        plt.ylabel( "Files from project1" )
        plt.grid(True)

        plt.show()


#-------------- test ---------------#
if __name__ == "__main__":
    file_map = {('file1', 'File1'): 1, ('file1', 'File3'): 3,
            ('file2', 'File2'): 1,
            ('file3', 'File1'): 5, ('file3', 'File2'): 4, ('file3', 'File3'): 2
           }
    myPlot = scatterPlot()

    for key, value in sorted(file_map.iteritems(), key=lambda (k,v): (v,k)):
        file1,file2 = key
        print file1,file2
        print value

        myPlot.set_value(file1,file2,value)

    myPlot.draw()
