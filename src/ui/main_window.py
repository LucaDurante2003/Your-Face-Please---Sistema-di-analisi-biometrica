"""
    Modulo per la finestra principale dell'applicazione
"""

import os
from PySide6.QtCore import Slot, Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QFrame)
from threads import VideoThread, WorkerThread

VALORE_DEFAULT = "-"

class MainWindow(QMainWindow):
    """
        Classe che rappresenta la finestra principale dell'applicazione
    """

    def __init__(self):
        """
            Funzione per inizializzare l'oggetto MainWindow
        """
        
        super().__init__()
        self.setWindowTitle("Your Face, Please")
        self.resize(1100, 650)

        path_icona = os.path.join(os.path.dirname(__file__), "img", "icon.png")
        if os.path.exists(path_icona):
            self.setWindowIcon(QIcon(path_icona))

        path_qss = os.path.join(os.path.dirname(__file__), "styles", "main_window.qss")
        if os.path.exists(path_qss):
            with open(path_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout_principale = QVBoxLayout(main_widget)
        layout_principale.setContentsMargins(0, 0, 0, 0)
        layout_principale.setSpacing(0)

        header = QWidget()
        header.setObjectName("header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        titolo = QLabel("DOCUMENTO DI RICONOSCIMENTO BIOMETRICO")
        titolo.setObjectName("header_titolo")
        header_layout.addWidget(titolo)
        layout_principale.addWidget(header)

        corpo = QHBoxLayout()
        corpo.setContentsMargins(15, 15, 15, 15)
        corpo.setSpacing(15)

        self.video_label = QLabel()
        self.video_label.setObjectName("video_label")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        corpo.addWidget(self.video_label, stretch=2)

        pannello_dati = QWidget()
        pannello_dati.setObjectName("pannello_dati")
        dati_layout = QVBoxLayout(pannello_dati)
        dati_layout.setContentsMargins(15, 10, 10, 10)
        dati_layout.setSpacing(5)

        sezione_titolo = QLabel("CONNOTATI E CONTRASSEGNI")
        sezione_titolo.setObjectName("sezione_titolo")
        dati_layout.addWidget(sezione_titolo)

        separatore = QFrame()
        separatore.setFrameShape(QFrame.Shape.HLine)
        separatore.setStyleSheet("color: #c0b090;")
        dati_layout.addWidget(separatore)

        campo_eta, self.valore_eta = self.crea_campo("ETÀ")
        dati_layout.addWidget(campo_eta)
        campo_genere, self.valore_genere = self.crea_campo("GENERE")
        dati_layout.addWidget(campo_genere)
        campo_occhi, self.valore_occhi = self.crea_campo("OCCHI")
        dati_layout.addWidget(campo_occhi)
        campo_capelli, self.valore_capelli = self.crea_campo("CAPELLI")
        dati_layout.addWidget(campo_capelli)
        campo_pelle, self.valore_pelle = self.crea_campo("INCARNATO")
        dati_layout.addWidget(campo_pelle)
        campo_espressione, self.valore_espressione = self.crea_campo("ESPRESSIONE")
        dati_layout.addWidget(campo_espressione)
        dati_layout.addStretch()

        self.btn_stop = QPushButton("TERMINA SESSIONE")
        self.btn_stop.setObjectName("btn_chiudi")
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self.close)
        dati_layout.addWidget(self.btn_stop)

        corpo.addWidget(pannello_dati, stretch=1)
        layout_principale.addLayout(corpo)

        self.timer_riconnessione = QTimer(self)
        self.timer_riconnessione.setInterval(3000)
        self.timer_riconnessione.timeout.connect(self.tenta_riconnessione)

        self.timer_nessun_volto = QTimer(self)
        self.timer_nessun_volto.setSingleShot(True)
        self.timer_nessun_volto.setInterval(3000)
        self.timer_nessun_volto.timeout.connect(self.reset_dashboard)

        self.avvia_worker_thread()
        self.avvia_video_thread()

    def crea_campo(self, testo_etichetta):
        """
            Funzione che crea un widget campo con etichetta e valore per la dashboard

            Args:
                testo_etichetta: testo dell'etichetta del campo
            
            Returns:
                tuple: (contenitore QWidget, QLabel del valore)
        """

        contenitore = QWidget()
        layout = QVBoxLayout(contenitore)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(2)

        etichetta = QLabel(testo_etichetta)
        etichetta.setProperty("ruolo", "etichetta")
        layout.addWidget(etichetta)

        valore = QLabel(VALORE_DEFAULT)
        valore.setProperty("ruolo", "valore")
        layout.addWidget(valore)

        return contenitore, valore
        
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
            self.video_thread.stop()
        
        self.video_thread = VideoThread()
        self.video_thread.frame_per_video.connect(self.aggiorna_video)
        self.video_thread.errore.connect(self.mostra_errore)
        self.video_thread.webcam_disconnessa.connect(self._webcam_disconnessa)
        self.video_thread.frame_per_analisi.connect(self.worker_thread.aggiorna_frame)
        self.video_thread.start()

    def avvia_worker_thread(self):
        """
            Funzione per avviare il worker thread
        """

        self.worker_thread = WorkerThread()
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
        self.reset_dashboard()
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

        self.valore_eta.setText(f"{dati['eta']} anni")
        self.valore_genere.setText(dati["genere"])
        self.valore_espressione.setText(dati["emozione"])
        self.valore_occhi.setText(dati.get("colore_occhi", "Non rilevato"))
        self.valore_capelli.setText(dati.get("colore_capelli", "Non rilevato"))
        self.valore_pelle.setText(dati.get("colore_pelle", "Non rilevato"))

        self.video_thread.imposta_regione_volto(dati.get("regione"))

    def reset_dashboard(self):
        """
            Funzione che reimposta la dashboard dei dati ai valori di default ed elimina il riquadro che rileva la regione del volto dal video
        """
        
        self.valore_eta.setText(VALORE_DEFAULT)
        self.valore_genere.setText(VALORE_DEFAULT)
        self.valore_espressione.setText(VALORE_DEFAULT)
        self.valore_occhi.setText(VALORE_DEFAULT)
        self.valore_capelli.setText(VALORE_DEFAULT)
        self.valore_pelle.setText(VALORE_DEFAULT)
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