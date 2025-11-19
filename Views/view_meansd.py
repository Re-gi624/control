# views/view_meansd.py
import os
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox

from widgets.mplwidget import MplWidget
from Logic.mean_sd import mean_sd_stats, plot_meansd_series, plot_hist


class MeanSDView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Cargar interfaz
        uic.loadUi(os.path.join("ui", "MeanSDView.ui"), self)

        # Estado interno
        self.df = None
        self.column_name = None

        # Embeder canvases en los placeholders
        self.canvas_chart = MplWidget(self.plotMeanSD)
        self._embed(self.plotMeanSD, self.canvas_chart)

        self.canvas_hist = MplWidget(self.histMeanSD)
        self._embed(self.histMeanSD, self.canvas_hist)

        # Conectar botón
        self.btnCalcMeanSD.clicked.connect(self.run_meansd)

    # ===============================================================
    # MÉTODOS DE SINCRONIZACIÓN CON EL MAINWINDOW
    # ===============================================================

    def set_data(self, df: pd.DataFrame, column_name: str):
        """Recibe datos desde MainWindow."""
        self.df = df
        self.column_name = column_name

    def clear_data(self):
        """Reset cuando no hay archivo cargado."""
        self.df = None
        self.column_name = None
        self.tblMeanSD.clear()
        self.canvas_chart.clear()
        self.canvas_hist.clear()

    def on_activated(self):
        """
        Se llama cuando el usuario cambia a la pestaña Mean-SD.
        Útil si algún día quieres refrescar algo automáticamente.
        """
        pass

    # ===============================================================
    # UTILIDAD: EMBEBER CANVAS
    # ===============================================================

    def _embed(self, placeholder, canvas):
        layout = QtWidgets.QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(canvas)

    # ===============================================================
    # BOTÓN PRINCIPAL
    # ===============================================================

    def run_meansd(self):
        """Ejecuta el cálculo total de Mean-SD."""
        if self.df is None or self.column_name is None:
            QMessageBox.warning(self, "Atención",
                "Primero carga un archivo y selecciona una columna numérica."
            )
            return

        # Obtener datos
        x = self.df[self.column_name].dropna().values

        try:
            df_stats = mean_sd_stats(x)
        except Exception as e:
            QMessageBox.critical(self, "Error en cálculo", str(e))
            return

        # Mostrar tabla
        self._fill_table(self.tblMeanSD, df_stats)

        # Control chart
        self.canvas_chart.clear()
        ax1 = self.canvas_chart.add_axes()
        plot_meansd_series(ax1, x)
        self.canvas_chart.draw()

        # Histograma
        self.canvas_hist.clear()
        ax2 = self.canvas_hist.add_axes()
        plot_hist(ax2, x)
        self.canvas_hist.draw()

    # ===============================================================
    # UTILIDAD: LLENAR TABLA
    # ===============================================================

    def _fill_table(self, table_widget, df: pd.DataFrame):
        table_widget.clear()
        table_widget.setColumnCount(df.shape[1])
        table_widget.setRowCount(df.shape[0])
        table_widget.setHorizontalHeaderLabels(df.columns.astype(str).tolist())

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                value = str(df.iat[i, j])
                table_widget.setItem(i, j, QtWidgets.QTableWidgetItem(value))

        table_widget.resizeColumnsToContents()
        table_widget.resizeRowsToContents()
