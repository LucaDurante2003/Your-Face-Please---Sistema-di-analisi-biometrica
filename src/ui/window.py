"""
Modulo per la finestra principale dell'applicazione
"""

import os
from PySide6.QtCore import Slot, Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton)
from src.threads.video_thread import VideoThread
from src.threads.worker_thread import WorkerThread

class MainWindow(QMainWindow):
    """
    Classe che rappresenta la finestra principale dell'applicazione
    """

    def __init__(self):
        """
        Funzione per inizializzare l'oggetto MainWindow
        """
        
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

        self.timer_riconnessione = QTimer(self)
        self.timer_riconnessione.setInterval(3000)
        self.timer_riconnessione.timeout.connect(self.tenta_riconnessione)

        self.timer_nessun_volto = QTimer(self)
        self.timer_nessun_volto.setSingleShot(True)
        self.timer_nessun_volto.setInterval(3000)
        self.timer_nessun_volto.timeout.connect(self.reset_dashboard)

        self.avvia_video_thread()
        self.avvia_worker_thread()
        
    def avvia_video_thread(self):
        """
        Funzione per avviare il video thread
        """

        if hasattr(self,'video_thread'):
            try:
                self.video_thread.frame_per_video.disconnect(self.aggiorna_video)
                self.video_thread.frame_per_analisi.disconnect()
                self.video_thread.errore.disconnect(self.mostra_errore)
                self.video_thread.webcam_disconnessa.disconnect(self._webcam_disconnessa)
            except RuntimeError:
                pass
        
        self.video_thread = VideoThread()
        self.video_thread.frame_per_video.connect(self.aggiorna_video)
        self.video_thread.errore.connect(self.mostra_errore)
        self.video_thread.webcam_disconnessa.connect(self._webcam_disconnessa)
        if hasattr(self,'worker_thread'):
            self.video_thread.frame_per_analisi.connect(self.worker_thread.aggiorna_frame)
        self.video_thread.start()

    def avvia_worker_thread(self):
        """
        Funzione per avviare il worker thread
        """

        self.worker_thread = WorkerThread()
        self.video_thread.frame_per_analisi.connect(self.worker_thread.aggiorna_frame)
        self.worker_thread.risultati_analisi.connect(self.aggiorna_dashboard)
        self.worker_thread.nessun_volto.connect(self.gestisci_nessun_volto)
        self.worker_thread.errore.connect(self.mostra_errore)
        self.worker_thread.start()


    @Slot(QImage)
    def aggiorna_video(self, image):
        """
        Funzione che riceve la nuova immagine e aggiorna il video mostrato nella GUI

        Args:
            image: nuova immagine con cui aggiornare la precedente
        """

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
    def mostra_errore(self, errore):
        """
        Funzione che riceve l'errore e lo mostra nella GUI

        Args:
            errore: errore da mostrare
        """

        self.statusBar().showMessage(errore)
    
    @Slot()
    def _webcam_disconnessa(self):
        """
        Funzione che riceve il segnale quando la webcam è irraggiungibile. Reimposta la dashboard dei dati
        """

        self.video_label.clear()
        self.video_label.setWordWrap(True)
        self.video_label.setText("Webcam disconnessa. \nRiconnessione in corso...")
        self.info_label.setText("<b>Dati rilevati</b><br>In attesa di rilevazione...")
        self.video_thread.imposta_regione_volto(None)
        if not self.timer_riconnessione.isActive():
            self.timer_riconnessione.start()

    @Slot()
    def gestisci_nessun_volto(self):
        """
        Funzione che riceve il segnale quando non viene più rilevato nessun volto. Gestisce il timer per il reset della dashboard dei dati
        """

        if not self.timer_nessun_volto.isActive():
            self.timer_nessun_volto.start()

    def aggiorna_dashboard(self, dati):
        """
        Funzione che riceve i risultati dell'analisi del volto e li mostra nella dashboard

        Args:
            dati: risultati dell'analisi del volto
        """

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
        """
        Funzione che reimposta la dashboard dei dati ed elimina il riquadro che rileva la regione del volto dal video
        """

        self.info_label.setText("<b>Dati rilevati</b><br>In attesa di rilevazione...")
        self.video_thread.imposta_regione_volto(None)

    def tenta_riconnessione(self):
        """
        Funzione che tenta di ristabilire la connessione con la webcam
        """

        if self.video_thread.isRunning():
            self.video_thread.stop()
            return
        self.avvia_video_thread()

    def closeEvent(self, event):
        """
        Funzione che viene chiamata quando la finestra viene chiusa. Ferma tutti i thread
        e chiude l'applicazione
        """
        
        self.timer_riconnessione.stop()
        self.timer_nessun_volto.stop()
        self.worker_thread.stop()
        self.video_thread.stop()
        super().closeEvent(event)