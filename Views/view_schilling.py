# views/view_schilling.py
import os
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox

from widgets.mplwidget import MplWidget
from Logic.schilling import calculate_schilling_plan


class SchillingView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Cargar archivo .ui
        uic.loadUi(os.path.join("ui", "SchillingView.ui"), self)

        # Estado interno
        self.df = None
        self.column_name = None
        self.sch_table_loaded = False

        # Incrustar canvas de Matplotlib en el contenedor "plotSchilling"
        self.canvas = MplWidget(self.plotSchilling)
        self._embed_canvas(self.plotSchilling, self.canvas)

        # Conectar botones
        self.btnLoadSchillingTable.clicked.connect(self.load_schilling_table)
        self.btnRunSchilling.clicked.connect(self.run_schilling)

    # =====================================================
    # MÉTODOS DE CONEXIÓN ENTRE MAINWINDOW Y ESTA VIEW
    # =====================================================

    def set_data(self, df: pd.DataFrame, column_name: str):
        """Llamado por MainWindow cuando cambia el archivo o la columna."""
        self.df = df
        self.column_name = column_name

    def clear_data(self):
        """Cuando no hay datos aún."""
        self.df = None
        self.column_name = None
        self.tblSchilling.clear()
        self.canvas.clear()

    def on_activated(self):
        """
        Opcional: cuando el usuario entra a esta vista en el QStackedWidget.
        Por si luego quieres refrescar algo automáticamente.
        """
        pass

    # =====================================================
    # UTILIDAD PARA EMBEBER LA GRÁFICA
    # =====================================================

    def _embed_canvas(self, placeholder, canvas):
        layout = QtWidgets.QVBoxLayout(placeholder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(canvas)

    # =====================================================
    # CARGAR TABLA SCHILLING (si algún día lo haces externo)
    # =====================================================

    def load_schilling_table(self):
        """
        ESTA FUNCIÓN SOLO SE DEJA POR SI QUIERES QUE TU PROFESORA TE SUBA UN CSV.
        PEERO: por ahora la tabla ya está embebida en logic/schilling.py.
        Así que solo actualiza la etiqueta.
        """
        self.lblSchillingTable.setText("Tabla Schilling integrada en lógica ✔")
        self.sch_table_loaded = True

    # =====================================================
    # BOTÓN PRINCIPAL: ANALIZAR SCHILLING
    # =====================================================

    def run_schilling(self):
        """Corre el análisis completo de Schilling."""
        if self.df is None or self.column_name is None:
            QMessageBox.warning(self, "Datos faltantes",
                                "Primero carga un archivo y selecciona una columna numérica.")
            return

        # ----------------------------------------------
        # Leer parámetros del usuario
        # ----------------------------------------------
        try:
            N = int(self.edN.text())
            LTPD = float(self.edLTPD.text())
            AQL = float(self.edAQL.text())  # aún no usado, pero se puede integrar
            LQL = float(self.edLQL.text())  # aún no usado, pero se puede integrar
        except ValueError:
            QMessageBox.warning(self, "Entrada inválida",
                                "Asegúrate de que AQL, LQL, N y LTPD sean números válidos.")
            return

        if N <= 0 or LTPD <= 0:
            QMessageBox.warning(self, "Valores inválidos",
                                "N y LTPD deben ser mayores que 0.")
            return

        # ----------------------------------------------
        # EJECUTAR LÓGICA REAL
        # ----------------------------------------------
        try:
            result = calculate_schilling_plan(N, LTPD)
        except Exception as e:
            QMessageBox.critical(self, "Error en cálculo", str(e))
            return

        # ----------------------------------------------
        # Mostrar tabla en la UI
        # ----------------------------------------------
        self._fill_table(self.tblSchilling, result["table"])

        # ----------------------------------------------
        # Graficar datos de la columna (histograma)
        # ----------------------------------------------
        x = self.df[self.column_name].dropna().values.astype(float)

        self.canvas.clear()
        ax = self.canvas.add_axes()

        # Histograma simple
        ax.hist(x, bins='auto', alpha=0.7, color='skyblue')
        media = np.mean(x)
        s = np.std(x, ddof=1)

        # Líneas de media ±3σ
        ax.axvline(media, color='black', linestyle='--', label=f"Media = {media:.3f}")
        ax.axvline(media + 3*s, color='red', linestyle='--', label="+3σ")
        ax.axvline(media - 3*s, color='red', linestyle='--', label="-3σ")

        ax.set_title(f"Datos de '{self.column_name}'")
        ax.set_xlabel("Valor")
        ax.set_ylabel("Frecuencia")
        ax.grid(True)
        ax.legend()

        self.canvas.draw()

    # =====================================================
    # UTILIDAD: LLENAR QTABLEWIDGET
    # =====================================================

    def _fill_table(self, table_widget, df: pd.DataFrame):
        table_widget.clear()
        table_widget.setColumnCount(df.shape[1])
        table_widget.setRowCount(df.shape[0])
        table_widget.setHorizontalHeaderLabels(df.columns.astype(str).tolist())

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                value = str(df.iat[row, col])
                table_widget.setItem(row, col, QtWidgets.QTableWidgetItem(value))

        table_widget.resizeColumnsToContents()
        table_widget.resizeRowsToContents()
