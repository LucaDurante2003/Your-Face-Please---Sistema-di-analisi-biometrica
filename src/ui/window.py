import os
from PySide6.QtCore import Slot, Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton)
from src.threads.video_thread import VideoThread
from src.threads.worker_thread import WorkerThread

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
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Parte sinistra (video)
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: #1e1e1e; color: white; border: 1px solid #d12626;")
        layout.addWidget(self.video_label, stretch=2)

        # Parte destra (dati)
        dashboard_dati = QVBoxLayout()
        self.info_label = QLabel("<b>Dati rilevati</b><br>In attesa di rilevazione...")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info_label.setStyleSheet("background-color: #1e1e1e; color: white; border: 1px solid #d12626;")
        dashboard_dati.addWidget(self.info_label)

        # Pulsante per arresto applicazione
        self.btn_stop = QPushButton("Arresta")
        self.btn_stop.clicked.connect(self.close)
        dashboard_dati.addWidget(self.btn_stop)
        layout.addLayout(dashboard_dati, stretch=1)

        # QTimer per la riconnessione automatica della webcam
        self.timer_riconnessione = QTimer(self)
        self.timer_riconnessione.setInterval(3000)
        self.timer_riconnessione.timeout.connect(self.tenta_riconnessione)

        # QTimer per resettare la dashboard in caso non venga rilevato più nessun volto
        self.timer_nessun_volto = QTimer(self)
        self.timer_nessun_volto.setSingleShot(True)
        self.timer_nessun_volto.setInterval(3000)
        self.timer_nessun_volto.timeout.connect(self.reset_dashboard)

        # Viene avviato il thread video e il thread worker
        self.avvia_video_thread()
        self.avvia_worker_thread()
        

    def avvia_video_thread(self):

        if hasattr(self,'video_thread'):
            try:
                self.video_thread.frame_per_video.disconnect(self.update_video)
                self.video_thread.frame_per_analisi.disconnect()
                self.video_thread.errore.disconnect(self.show_error)
                self.video_thread.webcam_disconnessa.disconnect(self._webcam_disconnessa)
            except RuntimeError:
                pass
        
        self.video_thread = VideoThread()
        self.video_thread.frame_per_video.connect(self.update_video)
        self.video_thread.errore.connect(self.show_error)
        self.video_thread.webcam_disconnessa.connect(self._webcam_disconnessa)
        if hasattr(self,'worker_thread'):
            self.video_thread.frame_per_analisi.connect(self.worker_thread.aggiorna_frame)
        self.video_thread.start()

    def avvia_worker_thread(self):
        self.worker_thread = WorkerThread()
        self.video_thread.frame_per_analisi.connect(self.worker_thread.aggiorna_frame)
        self.worker_thread.risultati_analisi.connect(self.aggiorna_dashboard)
        self.worker_thread.nessun_volto.connect(self.gestisci_nessun_volto)
        self.worker_thread.errore.connect(self.show_error)
        self.worker_thread.start()


    @Slot(QImage)
    def update_video(self, image: QImage): # slot per ricevere la nuova immagine e aggiornare il video

        if self.timer_riconnessione.isActive():
            self.timer_riconnessione.stop()
            self.statusBar().showMessage("La webcam è raggiungibile", 3000)

        scaled_pixmap = QPixmap.fromImage(image).scaled(
            self.video_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.FastTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    @Slot(str)
    def show_error(self, errore: str): # slot per ricevere l'errore e mostrarlo nella finestra
        self.statusBar().showMessage(errore)
    
    @Slot()
    def _webcam_disconnessa(self): # slot per ricevere il segnale quando la webcam è irraggiungibile
        self.video_label.clear()
        self.video_label.setWordWrap(True)
        self.video_label.setText("Webcam disconnessa. \nRiconnessione in corso...")
        self.info_label.setText("<b>Dati rilevati</b><br>In attesa di rilevazione...")
        self.video_thread.imposta_regione_volto(None)
        if not self.timer_riconnessione.isActive():
            self.timer_riconnessione.start()

    @Slot()
    def gestisci_nessun_volto(self): # slot per ricevere il segnale quando non viene rilevato più nessun volto
        if not self.timer_nessun_volto.isActive():
            self.timer_nessun_volto.start()

    def aggiorna_dashboard(self, dati):
        self.timer_nessun_volto.stop()
        testo = (
            f"<b>Dati rilevati</b><br><br>"
            f"<b>Età:</b> {dati['eta']} anni<br>"
            f"<b>Genere:</b> {dati['genere']}<br>"
            f"<b>Espressione:</b> {dati['emozione']}<br>"
        )
        self.info_label.setText(testo)
        self.video_thread.imposta_regione_volto(dati.get("regione"))

    def reset_dashboard(self):
        self.info_label.setText("<b>Dati rilevati</b><br>In attesa di rilevazione...")
        self.video_thread.imposta_regione_volto(None)

    def tenta_riconnessione(self):
        if self.video_thread.isRunning():
            self.video_thread.stop()
            return
        self.avvia_video_thread()

    def closeEvent(self, event):
        self.timer_riconnessione.stop()
        self.timer_nessun_volto.stop()
        self.worker_thread.stop()
        self.video_thread.stop()
        super().closeEvent(event)