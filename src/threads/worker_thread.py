"""
    Modulo per catturare un frame ogni 5 frame mandati dal VideoThread e analizzarlo
"""

from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
from src.engine.face_recognition import analizza_volto

class WorkerThread(QThread):
    """
        Classe che rappresenta un thread che lavora per ottenere e far analizzare i frame del flusso video
    """

    risultati_analisi = Signal(dict)
    errore = Signal(str)
    nessun_volto = Signal()

    def __init__(self, parent=None):
        """
            Funzione per inizializzare l'oggetto WorkerThread

            Args:
                parent: oggetto genitore
        """

        super().__init__(parent)
        self.is_running = True
        self.mutex = QMutex()
        self.condizione = QWaitCondition()
        self.frame_corrente = None
    
    def aggiorna_frame(self, frame):
        """
            Funzione che riceve un frame dal video thread e lo salva

            Args:
                frame: frame da salvare
        """
        self.mutex.lock()
        self.frame_corrente = frame.copy()
        self.condizione.wakeOne()
        self.mutex.unlock()

    def run(self):
        """
            Funzione che acquisisce i frame passati dal video thread, li fa analizzare
            e poi emette il risultato alla GUI
        """

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
        """
            Funzione per fermare il thread
        """

        self.is_running = False
        self.mutex.lock()
        self.condizione.wakeOne()
        self.mutex.unlock()
        self.quit()
        self.wait()