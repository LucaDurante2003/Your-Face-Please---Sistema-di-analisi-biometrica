from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
from src.engine.face_recognition import analizza_volto

class WorkerThread(QThread):

    risultati_analisi = Signal(dict)
    errore = Signal(str)
    nessun_volto = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = True
        self.mutex = QMutex()
        self.condizione = QWaitCondition()
        self.frame_corrente = None
    
    def aggiorna_frame(self, frame):
        self.mutex.lock()
        self.frame_corrente = frame.copy()
        self.condizione.wakeOne()
        self.mutex.unlock()

    def run(self):

        while self.is_running:
            self.mutex.lock()
            if self.frame_corrente is None:
                self.condizione.wait(self.mutex)
            frame = self.frame_corrente
            self.frame_corrente = None
            self.mutex.unlock()

            if frame is None or not self.is_running:
                continue

            try:
                risultato = analizza_volto(frame)
                if risultato is not None:
                    self.risultati_analisi.emit(risultato)
                else:
                    self.nessun_volto.emit()
            except Exception:
                self.errore.emit("Errore nell'analisi")
            finally:
                del frame
    
    def stop(self):
        self.is_running = False
        self.mutex.lock()
        self.condizione.wakeOne()
        self.mutex.unlock()
        self.quit()
        self.wait()