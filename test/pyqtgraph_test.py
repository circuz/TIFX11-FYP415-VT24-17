import pyqtgraph as pg
import numpy as np

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
    # size=(np.random.random(n) * 20.).astype(int),
    # brush=[pg.mkBrush(x) for x in np.random.randint(0, 256, (n, 3))],
    data=np.arange(n)
)
w4.addItem(s4)
s4.sigClicked.connect(clicked)

