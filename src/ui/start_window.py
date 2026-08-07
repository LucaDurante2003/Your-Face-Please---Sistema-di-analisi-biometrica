"""
    Modulo per la finestra di avvio dell'applicazione
"""

import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy)
from src.ui.main_window import MainWindow

class StartWindow(QMainWindow):
    """
        Classe che rappresenta la finestra di avvio dell'applicazione
    """

    def __init__(self):
        """
            Funzione per inizializzare l'oggetto StartWindow
        """

        super().__init__()
        self.setWindowTitle("Your Face, Please")
        self.setFixedSize(500, 400)

        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        path_icona = os.path.join(base, "img", "window.ico")

        if os.path.exists(path_icona):
            self.setWindowIcon(QIcon(path_icona))

        path_qss = os.path.join(os.path.dirname(__file__), "styles", "start_window.qss")
        with open(path_qss, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        titolo = QLabel("YOUR FACE,\nPLEASE")
        titolo.setObjectName("titolo")
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titolo)

        sottotitolo = QLabel("RILEVATORE BIOMETRICO")
        sottotitolo.setObjectName("sottotitolo")
        sottotitolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sottotitolo)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        linea_sopra = QLabel("─" * 30)
        linea_sopra.setObjectName("linea_decorativa")
        linea_sopra.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(linea_sopra)

        btn_inizia = QPushButton("INIZIA")
        btn_inizia.setObjectName("btn_inizia")
        btn_inizia.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_inizia.setFixedSize(200, 50)
        btn_inizia.clicked.connect(self.avvia_analisi)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_inizia)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        linea_sotto = QLabel("─" * 30)
        linea_sotto.setObjectName("linea_decorativa")
        linea_sotto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(linea_sotto)

        layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.finestra_analisi = None

    def avvia_analisi(self):
        """
            Funzione che apre la finestra principale e chiude la finestra di avvio
        """

        self.finestra_analisi = MainWindow()
        self.finestra_analisi.show()
        self.close()