"""
    Modulo per analizzare il frame passato dal worker thread ed effettuare l'analisi facciale
"""

from deepface import DeepFace
from retinaface import RetinaFace
import cv2
import logging

logger = logging.getLogger(__name__)

GENERE_ITA = { 
    "Man":"Uomo",
    "Woman":"Donna",
}

EMOZIONI_ITA = {
    "angry": "Arrabbiato",
    "disgust": "Disgustato",
    "fear": "Spaventato",
    "happy": "Felice",
    "sad": "Triste",
    "surprise": "Sorpreso",
    "neutral": "Neutro",
}

def analizza_volto(frame, larghezza_downscaling=320):
    """
        Funzione che riceve il frame passato dal worker thread e lo passa al modello di DeepFace, il quale lo analizza e fornisce i risultati

        Args:
            frame: frame passato dal worker thread
    
        Returns:
            dict: dizionario con i risultati di interesse (età, genere, emozione, regione)
    """

    frame_downscaling = None
    ritaglio_volto = None
    frame_creato_qui = False
    try:
        altezza_originale, larghezza_originale = frame.shape[:2]
        if larghezza_originale <= larghezza_downscaling:
            frame_downscaling = frame
            scala = 1.0
        else:
            scala = larghezza_originale / larghezza_downscaling
            altezza_downscaling = int(altezza_originale / scala)
            frame_downscaling = cv2.resize(frame, (larghezza_downscaling, altezza_downscaling))
            frame_creato_qui = True

        volti = RetinaFace.detect_faces(frame_downscaling)

        if not volti or not isinstance(volti,dict):
            return None
        
        chiave_primo_volto = list(volti.keys())[0]
        dati_primo_volto = volti[chiave_primo_volto]
        confidenza = dati_primo_volto.get("score",0)

        if confidenza < 0.5:
            return None

        regione_downscaling = dati_primo_volto.get("facial_area",[])

        if not regione_downscaling:
            return None

        x1, y1, x2, y2 = regione_downscaling
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame_downscaling.shape[1], x2)
        y2 = min(frame_downscaling.shape[0], y2)

        if x2 <= x1 or y2 <= y1:
            return None
            
        ritaglio_volto = frame_downscaling[y1:y2, x1:x2]

        if ritaglio_volto.size == 0:
            return None

        regione = {
            "x": int(x1 * scala),
            "y": int(y1 * scala),
            "w": int((x2 - x1) * scala),
            "h": int((y2 - y1) * scala),
        }

        landmarks_downscaling = dati_primo_volto.get("landmarks",{})
        landmarks = {}
        if not landmarks_downscaling:
            return None
        for nome, coordinate in landmarks_downscaling.items():
            landmarks[nome] = [
                int(coordinate[0] * scala),
                int(coordinate[1] * scala),
            ]
        
        risultati = DeepFace.analyze(
            img_path=ritaglio_volto,
            actions=["age","gender","emotion"],
            detector_backend="skip",
            enforce_detection=False,
            silent=True
        )
        
        if not risultati:
            return None

        if isinstance(risultati,list):
            volto = risultati[0]
        else:
            volto = risultati
        
        genere = volto.get("dominant_gender","")
        emozione = volto.get("dominant_emotion","")
        eta = int(volto.get("age",0))

        return {
            "eta": eta,
            "genere": GENERE_ITA.get(genere, "Non rilevato"),
            "emozione": EMOZIONI_ITA.get(emozione, "Non rilevata"),
            "regione": regione,
            "landmarks": landmarks
        }

    except Exception as e:
        logger.error("Errore nell'analisi del volto: %s", e, exc_info=True)
        return None
    
    finally:
        if ritaglio_volto is not None:
            del ritaglio_volto
        if frame_creato_qui and frame_downscaling is not None:
            frame_downscaling.fill(0)
            del frame_downscaling