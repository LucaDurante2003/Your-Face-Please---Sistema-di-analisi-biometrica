"""
    Modulo che funge da entrypoint per l'applicazione
"""

from PySide6.QtWidgets import QApplication
import sys
from src.ui.window import MainWindow
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())