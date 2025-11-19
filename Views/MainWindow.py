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

        self.mean_view = MeanSDView(parent=self)        
        self.schilling_view = SchillingView(parent=self)  

        # Estado compartido
        self.df = None              # DataFrame con los datos cargados
        self.current_column = None  # Nombre de la columna seleccionada

        # Conectar señales de la parte superior
        self.btnOpenFile.clicked.connect(self.on_open_file)
        self.cbColumn.currentIndexChanged.connect(self.on_column_changed)

        # Conectar los botones de selección de análisis
        self.btnMeanSD.clicked.connect(self.on_select_meansd)
        self.btnSchilling.clicked.connect(self.on_select_schilling)

        

        self.stackedViews.addWidget(self.mean_view)      
        self.stackedViews.addWidget(self.schilling_view) 

        # Pantalla inicial
        self.stackedViews.setCurrentIndex(0)
        self.statusbar.showMessage("Listo. Carga un archivo para comenzar.")

    # ==========================
    # Manejo de archivo de datos
    # ==========================

    def on_open_file(self):
        """Abrir CSV/Excel y cargarlo en un DataFrame compartido."""
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

        # Mostrar nombre de archivo
        self.lblFileName.setText(os.path.basename(path))

        # Llenar combo con columnas numéricas
        self.cbColumn.clear()
        if self.df is not None:
            numeric_cols = [
                c for c in self.df.columns
                if pd.api.types.is_numeric_dtype(self.df[c])
            ]
            self.cbColumn.addItems(numeric_cols)

        # Reset columna seleccionada
        self.current_column = self.cbColumn.currentText() if self.cbColumn.count() > 0 else None

        if self.df is not None and self.current_column:
            msg = f"Archivo cargado: {os.path.basename(path)}. Columna seleccionada: {self.current_column}"
        else:
            msg = f"Archivo cargado: {os.path.basename(path)}, pero no hay columnas numéricas."
        self.statusbar.showMessage(msg)

        # Avisar a las vistas (por si quieren reaccionar al cambio de df)
        self._propagate_data_to_views()

    def on_column_changed(self, index: int):
        """Actualizar la columna numérica seleccionada y avisar a las vistas."""
        if index < 0:
            self.current_column = None
        else:
            self.current_column = self.cbColumn.currentText()

        if self.df is not None and self.current_column:
            self.statusbar.showMessage(
                f"Columna seleccionada: {self.current_column}"
            )
        self._propagate_data_to_views()

    # ==================
    # Cambio de análisis
    # ==================

    def on_select_meansd(self):
        """Cambiar a la vista Mean-SD"""
        if not self._validate_data_available():
            return
        self.stackedViews.setCurrentWidget(self.mean_view)
        # Por si la vista quiere actualizar algo cuando se muestra
        if hasattr(self.mean_view, "on_activated"):
            self.mean_view.on_activated()

    def on_select_schilling(self):
        """Cambiar a la vista Schilling """
        if not self._validate_data_available():
            return
        self.stackedViews.setCurrentWidget(self.schilling_view)
        if hasattr(self.schilling_view, "on_activated"):
            self.schilling_view.on_activated()

    # =====================
    # Utilidades internas
    # =====================

    def _validate_data_available(self) -> bool:
        
        if self.df is None:
            QMessageBox.warning(self, "Atención", "Primero carga un archivo CSV/Excel.")
            return False
        if not self.current_column:
            QMessageBox.warning(self, "Atención", "Selecciona una columna numérica.")
            return False
        return True

    def _propagate_data_to_views(self):
        """
        Pasa df + nombre de columna a las vistas 
        """
        if self.df is None or not self.current_column:
            # Aun sin datos válidos
            if hasattr(self.mean_view, "clear_data"):
                self.mean_view.clear_data()
            if hasattr(self.schilling_view, "clear_data"):
                self.schilling_view.clear_data()
            return

        if hasattr(self.mean_view, "set_data"):
            self.mean_view.set_data(self.df, self.current_column)
        if hasattr(self.schilling_view, "set_data"):
            self.schilling_view.set_data(self.df, self.current_column)
