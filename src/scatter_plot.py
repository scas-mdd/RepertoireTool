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


    def draw(self):
        X = self.x.data
        Y = self.y.data

        plt.scatter(X,Y,c=self.color_map)
        plt.xticks(range(len(X)),self.x.label,size='small')
        plt.yticks(range(len(Y)),self.y.label,size='small')

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
