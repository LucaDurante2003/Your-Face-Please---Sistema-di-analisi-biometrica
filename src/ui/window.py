import os
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton)
from src.threads.video_thread import VideoThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rilevatore biometrico")
        self.resize(1000, 600)

        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        path = os.path.join(base,"img","window.ico")

        if os.path.exists(path):
            self.setWindowIcon(QIcon(path))

        # Layout
        main_widget = QWidget() # contenitore vuoto generico
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Parte sinistra (video)
        self.video_label = QLabel("Avvio webcam in corso...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: #1e1e1e; color: white; border: 1px solid #d12626;")
        layout.addWidget(self.video_label, stretch=2)

        # Parte destra (dati)
        dashboard_layout = QVBoxLayout()
        self.info_label = QLabel("<b>Dati rilevati</b><br>In attesa di rilevazione...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info_label.setStyleSheet("background-color: #1e1e1e; color: white; border: 1px solid #d12626;")
        dashboard_layout.addWidget(self.info_label)

        # Pulsante per arresto applicazione
        self.btn_stop = QPushButton("Arresta")
        self.btn_stop.clicked.connect(self.close_application)
        dashboard_layout.addWidget(self.btn_stop)
        layout.addLayout(dashboard_layout, stretch=1)

        # Viene avviato il thread video
        self.video_thread = VideoThread()
        self.video_thread.frame_catturato.connect(self.update_video)
        self.video_thread.errore.connect(self.show_error)
        self.video_thread.start()

    @Slot(QImage)
    def update_video(self, image: QImage): # slot per ricevere la nuova immagine e aggiornare il video

        scaled_pixmap = QPixmap.fromImage(image).scaled(
            self.video_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.FastTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    @Slot(str)
    def show_error(self, errore: str): # slot per ricevere l'errore e mostrarlo nella finestra
        self.info_label.setText(f"<b>Errore</b><br>{errore}")
    
    def close_application(self): # collegato al pulsante "Arresta"
        self.close()

    def closeEvent(self, event):
        self.video_thread.stop()
        super().closeEvent(event)