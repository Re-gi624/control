# Views/view_meansd.py
import os
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox

from widgets.mplwidget import MplWidget
from Logic.xbar_s import xbar_s_analysis


class MeanSDView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi(os.path.join("ui", "MeanSDView.ui"), self)

        self.df = None
        self.numeric_df = None

        # Canvases
        self.canvas_xbar = MplWidget(self.plotMeanSD)
        self._embed(self.plotMeanSD, self.canvas_xbar)

        self.canvas_s = MplWidget(self.histMeanSD)
        self._embed(self.histMeanSD, self.canvas_s)

        self.btnCalcMeanSD.clicked.connect(self.run_xbar_s)

    # --------------------------------------------------------------------
    def _embed(self, placeholder, canvas):
        layout = QtWidgets.QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(canvas)

    # --------------------------------------------------------------------
    def set_data(self, df: pd.DataFrame, _column_name: str):
        """
        Procesa datos asegurando que TODO esté convertido a float
        y que la columna SUBGROUP no entre en el cálculo.
        """
        self.df = df

        # 1. Convertir todas las columnas a número (sanitización completa)
        numeric_df = df.apply(pd.to_numeric, errors="coerce")

        # 2. Eliminar columna SUBGROUP explícitamente
        for col in list(numeric_df.columns):
            name = str(col).strip().upper()
            if name in ("SUBGROUP", "SUBGRUPO", "SUBGROUPS"):
                numeric_df.drop(columns=[col], inplace=True)

        # 3. Eliminar columnas totalmente vacías
        numeric_df = numeric_df.dropna(axis=1, how="all")

        # 4. Asegurar float REAL para cálculos
        numeric_df = numeric_df.astype(float)

        self.numeric_df = numeric_df

    # --------------------------------------------------------------------
    def clear_data(self):
        self.df = None
        self.numeric_df = None
        self.tblMeanSD.clear()
        self.canvas_xbar.clear()
        self.canvas_s.clear()

    def on_activated(self):
        pass

    # --------------------------------------------------------------------
    def run_xbar_s(self):
        if self.numeric_df is None or self.numeric_df.empty:
            QMessageBox.warning(
                self, "Datos insuficientes",
                "Carga un archivo con varias columnas numéricas."
            )
            return

        if self.numeric_df.shape[1] < 2:
            QMessageBox.warning(
                self, "Subgrupos inválidos",
                "Se necesitan al menos 2 columnas numéricas (tamaño del subgrupo >= 2)."
            )
            return

        try:
            result = xbar_s_analysis(self.numeric_df)
            print("\n=== DATOS QUE ESTÁ LEYENDO PARA CALCULAR ===")
            print(self.numeric_df.head(20))


        except Exception as e:
            QMessageBox.critical(self, "Error en cálculo", str(e))
            return

        self._fill_table(self.tblMeanSD, result["summary"])
        self._plot_xbar(result)
        self._plot_s(result)

    # --------------------------------------------------------------------
    # GRÁFICO X-BAR FINAL
    # --------------------------------------------------------------------
    def _plot_xbar(self, r):
        self.canvas_xbar.clear()
        ax = self.canvas_xbar.add_axes()

        x = np.arange(1, len(r["xbar_i"]) + 1)
        y = r["xbar_i"]

        ax.plot(x, y, marker="o", linestyle="-", label="X̄_i")

        ax.axhline(r["ucl_x"], color="red", linestyle="--",
                   label=f"UCL_X = {r['ucl_x']:.4f}")
        ax.axhline(r["cl_x"], color="green", linestyle="--",
                   label=f"CL_X = {r['cl_x']:.4f}")
        ax.axhline(r["lcl_x"], color="red", linestyle="--",
                   label=f"LCL_X = {r['lcl_x']:.4f}")

        ax.set_title("Gráfico X̄ (medias por subgrupo)")
        ax.set_xlabel("Subgrupo")
        ax.set_ylabel("Media X̄_i")
        ax.grid(True)
        ax.legend()

        self.canvas_xbar.draw()

    # --------------------------------------------------------------------
    # GRÁFICO S FINAL
    # --------------------------------------------------------------------
    def _plot_s(self, r):
        self.canvas_s.clear()
        ax = self.canvas_s.add_axes()

        x = np.arange(1, len(r["s_i"]) + 1)
        y = r["s_i"]

        ax.plot(x, y, marker="o", linestyle="-", label="S_i")

        ax.axhline(r["ucl_s"], color="red", linestyle="--",
                   label=f"UCL_S = {r['ucl_s']:.4f}")
        ax.axhline(r["cl_s"], color="green", linestyle="--",
                   label=f"CL_S = {r['cl_s']:.4f}")
        ax.axhline(r["lcl_s"], color="red", linestyle="--",
                   label=f"LCL_S = {r['lcl_s']:.4f}")

        ax.set_title("Gráfico S (desv. estándar por subgrupo)")
        ax.set_xlabel("Subgrupo")
        ax.set_ylabel("S_i")
        ax.grid(True)
        ax.legend()

        self.canvas_s.draw()

    # --------------------------------------------------------------------
    # TABLA RESUMEN
    # --------------------------------------------------------------------
    def _fill_table(self, table_widget, df: pd.DataFrame):
        table_widget.clear()
        table_widget.setColumnCount(df.shape[1])
        table_widget.setRowCount(df.shape[0])
        table_widget.setHorizontalHeaderLabels(df.columns.astype(str).tolist())

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                val = str(df.iat[i, j])
                table_widget.setItem(i, j, QtWidgets.QTableWidgetItem(val))

        table_widget.resizeColumnsToContents()
        table_widget.resizeRowsToContents()
