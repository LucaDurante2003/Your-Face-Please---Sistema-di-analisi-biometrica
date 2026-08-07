"""
    Modulo per catturare il flusso video da mostrare nel riquadro sinistro dell'applicazione
"""

import cv2
from PySide6.QtCore import QThread, Signal, QMutex
from PySide6.QtGui import QImage
import logging

logger = logging.getLogger(__name__)

class VideoThread(QThread):
    """
        Classe che rappresenta un thread che lavora per catturare e mostrare il flusso video della webcam
    """

    frame_per_video = Signal(QImage) 
    frame_per_analisi = Signal(object)
    errore= Signal(str)
    webcam_disconnessa = Signal()

    def __init__(self, indice_camera=0, parent=None):
        """
            Funzione per inizializzare l'oggetto VideoThread

            Args:
                indice_camera: int che indica quale webcam selezionare
                parent: oggetto genitore
        """

        super().__init__(parent)
        self.indice_camera = indice_camera
        self.is_running = True
        self.contatore_frame = 0
        self.regione_volto = None
        self.mutex_regione = QMutex()

    def imposta_regione_volto(self, regione):
        """
            Funzione per impostare la regione del volto

            Args:
                regione: coordinate del volto rilevato
        """

        self.mutex_regione.lock()
        self.regione_volto = regione
        self.mutex_regione.unlock()

    def run(self):
        """ 
            Funzione che acquisisce i frame dalla webcam, li invia al worker thread per l'analisi e li mostra nel riquadro sinistro
        """
        
        cap = None
        try:
            cap = cv2.VideoCapture(self.indice_camera)
            cap.set(cv2.CAP_PROP_FPS, 30)
            if not cap.isOpened():
                self.errore.emit("La webcam è irraggiungibile")
                self.webcam_disconnessa.emit()
                return
            errori_consecutivi = 0
            while self.is_running:
                ret, frame = cap.read()
                if not ret or frame is None:
                    errori_consecutivi += 1
                    if errori_consecutivi > 30:
                        self.errore.emit("La webcam è irraggiungibile")
                        self.webcam_disconnessa.emit()
                        break
                    self.msleep(100)
                    continue
                errori_consecutivi = 0

                self.contatore_frame += 1
                if self.contatore_frame >= 5:
                    self.contatore_frame = 0
                    self.frame_per_analisi.emit(frame)

                self.mutex_regione.lock()
                regione = self.regione_volto
                self.mutex_regione.unlock()
                if regione is not None:
                    x = regione["x"]
                    y = regione["y"]
                    w = regione["w"]
                    h = regione["h"]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                try:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                except cv2.error as e:
                    logger.error("Errore nella conversione del colore: %s", e, exc_info=True)
                    self.errore.emit("Conversione colore non andata a buon fine")
                    continue
            
                h_img, w_img, ch_img = rgb_frame.shape
                bytes_per_linea = ch_img * w_img
                dati = rgb_frame.tobytes()
                immagine_qt = QImage(dati, w_img, h_img, bytes_per_linea, QImage.Format.Format_RGB888).copy()
                self.frame_per_video.emit(immagine_qt)
                
                del frame
                del rgb_frame
                self.msleep(33)
        except Exception as e:
            logger.error("Errore nel VideoThread: %s", e, exc_info=True)
            self.errore.emit("Problema nel VideoThread")

        finally:
            if cap is not None:
                cap.release()

    def stop(self):
        """
            Funzione per fermare il thread
        """
        
        self.is_running = False
        self.quit()
        self.wait()