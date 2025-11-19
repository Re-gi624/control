# views/view_schilling.py
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox

from Widgets.mplwidget import MplWidget
from Logic.schilling import calculate_schilling_plan


class SchillingView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi(os.path.join("ui", "SchillingView.ui"), self)

        # Gráfica
        self.canvas = MplWidget(self.plotSchilling)
        self._embed(self.plotSchilling, self.canvas)

        # Sin archivo
        self.lblTitle.setText("Análisis Schilling (solo N y LTPD)")

        self.btnRunSchilling.clicked.connect(self.run_schilling)

    # Embebido del canvas
    def _embed(self, placeholder, canvas):
        layout = QtWidgets.QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(canvas)

    # --------------------------------------------------------
    # EJECUTAR SCHILLING 
    # --------------------------------------------------------
    def run_schilling(self):
        try:
            N = int(self.edN.text())
            LTPD = float(self.edLTPD.text())
        except:
            QMessageBox.warning(self, "Error", "N debe ser entero y LTPD debe ser decimal.")
            return

        if N <= 0 or LTPD <= 0:
            QMessageBox.warning(self, "Error", "N y LTPD deben ser mayores que 0.")
            return

        # Ejecutar lógica
        result = calculate_schilling_plan(N, LTPD)

        # Mostrar tabla
        self._fill_table(self.tblSchilling, result["table"])

        # Mostrar gráfico simple basado en K y f
        self._plot_schilling(result)

   
    def _plot_schilling(self, r):
        self.canvas.clear()
        ax = self.canvas.add_axes()

        # punto único
        ax.scatter([r["K"]], [r["f_total"]], color="blue", s=80)

        ax.axhline(r["f_total"], color="green", linestyle="--", label=f"f = {r['f_total']:.3f}")
        ax.axvline(r["K"], color="red", linestyle="--", label=f"K = {r['K']:.3f}")

        ax.set_title(f"Schilling — n = {r['n_final']}")
        ax.set_xlabel("K = N * LTPD")
        ax.set_ylabel("f_total")
        ax.grid(True)
        ax.legend()

        self.canvas.draw()

   
    def _fill_table(self, table_widget, df):
        table_widget.clear()
        table_widget.setColumnCount(df.shape[1])
        table_widget.setRowCount(df.shape[0])
        table_widget.setHorizontalHeaderLabels(df.columns.astype(str).tolist())

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                table_widget.setItem(i, j, QtWidgets.QTableWidgetItem(str(df.iat[i, j])))

        table_widget.resizeColumnsToContents()
        table_widget.resizeRowsToContents()
