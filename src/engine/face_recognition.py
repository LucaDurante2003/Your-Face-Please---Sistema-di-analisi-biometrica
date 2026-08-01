"""
Modulo per analizzare il frame passato dal worker thread ed effettuare il riconoscimento facciale
"""

from deepface import DeepFace
import cv2

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

def analizza_volto(frame):
    """
    Funzione che riceve il frame passato dal worker thread e lo passa al modello di DeepFace, il quale lo analizza e fornisce i risultati

    Args:
        frame: frame passato dal worker thread
    
    Returns:
        dict: dizionario con i risultati di interesse (età, genere, emozione, regione)
    """

    try:
        altezza_originale, larghezza_originale = frame.shape[:2]
        larghezza_downscaling = 320
        scala = larghezza_originale / larghezza_downscaling
        altezza_downscaling = int(altezza_originale / scala)
        frame_downscaling = cv2.resize(frame, (larghezza_downscaling, altezza_downscaling))

        risultati = DeepFace.analyze(
            img_path=frame_downscaling,
            actions=["age","gender","emotion"],
            detector_backend="retinaface",
            enforce_detection=False,
            silent=True
        )
        
        if not risultati:
            return None

        if isinstance(risultati,list):
            volto = risultati[0]
        else:
            volto = risultati
        
        confidenza = volto.get("face_confidence",0)

        if confidenza < 0.5:
            return None

        regione_downscaling = volto.get("region",{})
        regione = {
            "x": int(regione_downscaling.get("x", 0) * scala),
            "y": int(regione_downscaling.get("y", 0) * scala),
            "w": int(regione_downscaling.get("w", 0) * scala),
            "h": int(regione_downscaling.get("h", 0) * scala),
        }
        genere = volto.get("dominant_gender","")
        emozione = volto.get("dominant_emotion","")
        eta = int(volto.get("age",0))

        return {
            "eta": eta,
            "genere": GENERE_ITA.get(genere),
            "emozione": EMOZIONI_ITA.get(emozione),
            "regione": regione
        }
    except Exception:
        return None
    
    finally:
        del frame