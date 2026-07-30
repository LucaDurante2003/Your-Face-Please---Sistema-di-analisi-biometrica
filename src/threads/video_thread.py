import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

class VideoThread(QThread):

    frame_per_video = Signal(QImage) # immagine catturata dalla webcam
    frame_per_analisi = Signal(object)
    errore= Signal(str) # messaggio di errore
    webcam_disconnessa = Signal() # segnale emesso quando la webcam è irraggiungibile

    def __init__(self, indice_camera=0, parent=None):
        super().__init__(parent)
        self.indice_camera = indice_camera # seleziona la webcam predefinita del computer
        self.is_running = True # controlla il while in run e, a differenza di while true, può essere controllato esternamente modificando questo parametro (funzione stop())
        self.contatore_frame = 0
        self.regione_volto = None

    def imposta_regione_volto(self, regione):
        self.regione_volto = regione

    def run(self):
        cap = None # oggetto che gestisce la connessione fisica alla webcam e attraverso la quale si possono impostare gli fps oppure leggere i frame
        try:
            cap = cv2.VideoCapture(self.indice_camera)
            cap.set(cv2.CAP_PROP_FPS, 30)
            if not cap.isOpened(): # si controlla se la webcam si apre o no
                self.errore.emit("La webcam è irraggiungibile")
                self.webcam_disconnessa.emit()
                return
            errori_consecutivi = 0
            while self.is_running: # qui inizia il ciclo di acquisizione
                ret, frame = cap.read() # ret è un booleano che indica se la lettura del frame è andata bene mentre frame è l'immagine sotto forma di array NumPy a 3 dimensioni
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
                    self.frame_per_analisi.emit(frame.copy())

                regione = self.regione_volto
                if regione is not None:
                    x = regione["x"]
                    y = regione["y"]
                    w = regione["w"]
                    h = regione["h"]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                try:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # conversione del frame da bgr a rgb
                except cv2.error:
                    self.errore.emit("Conversione colore non andata a buon fine")
                    continue
            
                h_img, w_img, ch = rgb_frame.shape
                bytes_per_linea = ch * w_img
                immagine_qt = QImage(rgb_frame.copy().data, w_img, h_img, bytes_per_linea, QImage.Format.Format_RGB888) # viene creato un oggetto QImage a partire dai dati dell'array NumPy
                self.frame_per_video.emit(immagine_qt)

                del frame
                del rgb_frame
                self.msleep(33)
        except Exception:
            self.errore.emit("Problema nel VideoThread")

        finally:
            if cap is not None:
                cap.release()

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()