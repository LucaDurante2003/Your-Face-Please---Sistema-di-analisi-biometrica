import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

class VideoThread(QThread):

    frame_catturato = Signal(QImage) # immagine catturata dalla webcam
    errore= Signal(str) # messaggio di errore

    def __init__(self, indice_camera=0, parent=None):
        super().__init__(parent)
        self.indice_camera = indice_camera # seleziona la webcam predefinita del computer
        self._is_running = True # controlla il while in run e, a differenza di while true, può essere controllato esternamente modificando questo parametro (funzione stop())

    def run(self):
        cap = None # oggetto che gestisce la connessione fisica alla webcam e attraverso la quale si possono impostare gli fps oppure leggere i frame
        try:
            cap = cv2.VideoCapture(self.indice_camera)
            cap.set(cv2.CAP_PROP_FPS, 30)
            if not cap.isOpened(): # si controlla se la webcam si apre o no
                self.errore.emit(f"Errore: la webcam non si apre (indice: {self.indice_camera})")
                return
            errori_consecutivi = 0
            while self._is_running: # qui inizia il ciclo di acquisizione
                ret, frame = cap.read() # ret è un booleano che indica se la lettura del frame è andata bene mentre frame è l'immagine sotto forma di array NumPy a 3 dimensioni
                if not ret or frame is None:
                    errori_consecutivi += 1
                    if errori_consecutivi > 30:
                        self.errore.emit("Errore: webcam irraggiungibile")
                        break # dopo più di 30 volte consecutive in cui non si riesce a leggere il frame, si esce dal ciclo while
                    continue # si salta questa iterazione e si ricomincia con una nuova
                errori_consecutivi = 0
                try:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # conversione del frame da bgr a rgb
                except cv2.error as e:
                    self.errore.emit(f"Errore: conversione colore:{e}")
                    continue
            
                h, w, ch = rgb_frame.shape
                bytes_per_linea = ch * w
                immagine_qt = QImage(rgb_frame.copy().data, w, h, bytes_per_linea, QImage.Format.Format_RGB888) # viene creato un oggetto QImage a partire dai dati dell'array NumPy
                self.frame_catturato.emit(immagine_qt.copy())

                del frame
                del rgb_frame
        except Exception as e:
            self.errore.emit(f"Errore: problema nel VideoThread: {e}")

        finally:
            if cap is not None:
                cap.release()

    def stop(self):
        self._is_running = False
        self.wait()




        # Da risolvere problema che si verifica quando l'app è aperta ma si scollega la webcam