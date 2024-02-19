"""
Example demonstrating a variety of scatter plot features.
"""

# from collections import namedtuple

import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtWidgets

app = pg.mkQApp("Scatter Plot Item Example") 
mw = QtWidgets.QMainWindow()
mw.resize(800,800)
view = pg.GraphicsLayoutWidget()  ## GraphicsView with GraphicsLayout inserted by default
mw.setCentralWidget(view)
mw.show()
mw.setWindowTitle('pyqtgraph example: ScatterPlot')

## create four areas to add plots
w1 = view.addPlot()
w2 = view.addViewBox()
w2.setAspectLocked(True)
view.nextRow()
w3 = view.addPlot()
w4 = view.addPlot()
print("Generating data, this takes a few seconds...")

## There are a few different ways we can draw scatter plots; each is optimized for different types of data:

## 1) All spots identical and transform-invariant (top-left plot).
## In this case we can get a huge performance boost by pre-rendering the spot
## image and just drawing that image repeatedly.

n = 300
s1 = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
pos = np.random.normal(size=(2,n), scale=1e-5)
spots = [{'pos': pos[:,i], 'data': 1} for i in range(n)] + [{'pos': [0,0], 'data': 1}]
s1.addPoints(spots)
w1.addItem(s1)

## Test performance of large scatterplots

s4 = pg.ScatterPlotItem(
    size=10,
    pen=pg.mkPen(None),
    brush=pg.mkBrush(255, 255, 255, 20),
    hoverable=True,
    hoverSymbol='s',
    hoverSize=15,
    hoverPen=pg.mkPen('r', width=2),
    hoverBrush=pg.mkBrush('g'),
)
n = 10000
pos = np.random.normal(size=(2, n), scale=1e-9)
s4.addPoints(
    x=pos[0],
    y=pos[1],
    size=(np.random.random(n) * 20.).astype(int),
    # brush=[pg.mkBrush(x) for x in np.random.randint(0, 256, (n, 3))],
    data=np.arange(n)
)
print(s4.data)
w4.addItem(s4)

if __name__ == '__main__':
    pg.exec()

