from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotWidget(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        self.fig = fig
        self.setParent(parent)
    
    def clear(self):
        self.fig.clf()
        self.draw()

    def add_axes(self):
        ax = self.fig.add_subplot(111)
        return ax