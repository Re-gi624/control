# widgets/mplwidget.py
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class MplWidget(QWidget):
    """
    Widget universal para incrustar figuras de Matplotlib en PyQt5.

    - canvas.fig      → figura completa
    - canvas.add_axes() → agrega un axis (limpia antes si quieres)
    - canvas.clear() → limpia toda la figura
    - canvas.draw()  → redibuja
    """

    def __init__(self, parent=None, width=5, height=3, dpi=100):
        super().__init__(parent)

        # Crear figura de Matplotlib
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvas(self.fig)

        # Layout para incrustar el canvas
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    # ------------------------------------------------------------
    # MÉTODO MÁS USADO → limpia y borra TODO el contenido del plot
    # ------------------------------------------------------------
    def clear(self):
        """Borra completamente la figura."""
        self.fig.clf()
        self.canvas.draw()

    # ------------------------------------------------------------
    # CREA UN NUEVO AXIS Y LO REGRESA
    # ------------------------------------------------------------
    def add_axes(self):
        """
        Crea un nuevo axis en la figura y lo devuelve.
        Esto te permite llamar:
            ax = widget.add_axes()
        """
        ax = self.fig.add_subplot(111)
        return ax

    # ------------------------------------------------------------
    # Redibujar (útil cuando haces cambios directos a self.fig)
    # ------------------------------------------------------------
    def draw(self):
        self.canvas.draw()
