# views/MainWindow.py
import os
import pandas as pd
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from Services.FileLoader import load_dataframe
from Views.view_meansd import MeanSDView
from Views.view_schilling import SchillingView


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Cargar el diseño del MainWindow
        uic.loadUi(os.path.join("ui", "MainView.ui"), self)

        # Crear vistas
        self.mean_view = MeanSDView(parent=self)
        self.schilling_view = SchillingView(parent=self)

        # Estado compartido SOLO para Mean-SD
        self.df = None
        self.current_column = None

        # Conectar señales de archivo
        self.btnOpenFile.clicked.connect(self.on_open_file)
        self.cbColumn.currentIndexChanged.connect(self.on_column_changed)

        # Conectar selección de análisis
        self.btnMeanSD.clicked.connect(self.on_select_meansd)
        self.btnSchilling.clicked.connect(self.on_select_schilling)

        # Agregar vistas al stacked
        self.stackedViews.addWidget(self.mean_view)
        self.stackedViews.addWidget(self.schilling_view)

        # Pantalla inicial
        self.stackedViews.setCurrentIndex(0)
        self.statusbar.showMessage("Listo. Carga un archivo para comenzar.")

    # ==========================================================
    # ABRIR ARCHIVO (solo para Mean-SD)
    # ==========================================================

    def on_open_file(self):
        """Abrir archivo CSV/Excel para Mean-SD."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo de datos",
            "",
            "Archivos de datos (*.csv *.xlsx *.xls)"
        )
        if not path:
            return

        try:
            self.df = load_dataframe(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer el archivo:\n{e}")
            return

        # Mostrar nombre del archivo
        self.lblFileName.setText(os.path.basename(path))

        # Llenar combo con columnas numéricas
        numeric_cols = [c for c in self.df.columns
                        if pd.api.types.is_numeric_dtype(self.df[c])]

        self.cbColumn.clear()
        self.cbColumn.addItems(numeric_cols)

        self.current_column = self.cbColumn.currentText() if numeric_cols else None

        # Mensaje de estado
        if self.current_column:
            msg = f"Archivo cargado: {os.path.basename(path)} | Columna numérica: {self.current_column}"
        else:
            msg = f"Archivo cargado: {os.path.basename(path)}, pero no hay columnas numéricas."
        self.statusbar.showMessage(msg)

        # Propagar SOLO a Mean-SD
        self._propagate_data_to_views()

    def on_column_changed(self, index: int):
        """Actualizar la columna seleccionada (solo Mean-SD)."""
        self.current_column = self.cbColumn.currentText() if index >= 0 else None
        self.statusbar.showMessage(f"Columna seleccionada: {self.current_column}")
        self._propagate_data_to_views()

    # ==========================================================
    # CAMBIO DE VISTAS
    # ==========================================================

    def on_select_meansd(self):
        """Cambiar a la vista Mean-SD. Esta sí requiere archivo."""
        if not self._validate_data_available():
            return

        self.stackedViews.setCurrentWidget(self.mean_view)

        if hasattr(self.mean_view, "on_activated"):
            self.mean_view.on_activated()

    def on_select_schilling(self):
        """
        Cambiar a la vista Schilling.
        ¡IMPORTANTE! → Schilling NO requiere archivo ni columna.
        """
        self.stackedViews.setCurrentWidget(self.schilling_view)
        self.statusbar.showMessage("Modo Schilling listo. No requiere archivo.")

        # No enviar df ni columna a Schilling
        if hasattr(self.schilling_view, "on_activated"):
            self.schilling_view.on_activated()

    # ==========================================================
    # VALIDACIÓN SOLO PARA MEAN-SD
    # ==========================================================

    def _validate_data_available(self) -> bool:
        """Mean-SD sí necesita archivo y columna."""
        if self.df is None:
            QMessageBox.warning(self, "Atención",
                                "Mean-SD requiere un archivo CSV/Excel.")
            return False
        if not self.current_column:
            QMessageBox.warning(self, "Atención",
                                "Selecciona una columna numérica.")
            return False
        return True

    # ==========================================================
    # ENVIAR DATOS SOLO A MEAN-SD
    # ==========================================================

    def _propagate_data_to_views(self):
        """
        Mean-SD sí recibe df y columna.
        Schilling NO recibe nada (por petición del usuario).
        """
        # Caso sin datos válidos
        if self.df is None or not self.current_column:
            if hasattr(self.mean_view, "clear_data"):
                self.mean_view.clear_data()
            return

        # Caso con datos válidos → enviar SOLO a MeanSD
        if hasattr(self.mean_view, "set_data"):
            self.mean_view.set_data(self.df, self.current_column)
