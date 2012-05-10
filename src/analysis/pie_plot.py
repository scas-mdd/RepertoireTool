from pylab import *
from matplotlib import font_manager as fm
from matplotlib.transforms import Affine2D
from matplotlib.patches import Circle, Wedge, Polygon
import numpy as np

class pieObj:
    def __init__(self,fracs,labels):
        self.fracList = fracs
        self.labelList = labels

    def draw(self):
        fig = plt.figure(facecolor='white', edgecolor='white')
        subplot_num = len(self.fracList)

        axes = [0] * subplot_num
        name = ['project 0','project 1']

        for i in range(subplot_num):
            #nasty stuff, need to fix this
            if i is 0:
                pos = 1
            else:
                pos = 4
            axes[i] = fig.add_subplot(subplot_num,subplot_num,pos)
            axes[i].set_title(name[i])
            patches, texts, autotexts = axes[i].pie(self.fracList[i], labels=self.labelList[i],autopct='%1.1f%%', shadow =False)
            proptease = fm.FontProperties()
            proptease.set_size('small')
            setp(autotexts, fontproperties=proptease)
            setp(texts, fontproperties=proptease)
            rcParams['legend.fontsize'] = 7.0
        plt.show()

#-------------test---------------#
if __name__ == "__main__":
    fracs = [[20, 7, 20, 15, 12, 8, 15],[8, 13, 11, 16, 31, 18]]
    labels = [['Parker', 'alex', 'Moore', 'Clark', 'Garcia', 'Green', 'Hall'], ['Lee', 'Johnson', 'Harris', 'Scott', 'Martin', 'White']]
    piePlot = pieObj(fracs,labels)
    piePlot.draw()

