from deepface import DeepFace
import numpy as numpy

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
    try:
        risultati = DeepFace.analyze(
            img_path=frame,
            actions=["age","gender","emotion"],
            detector_backend="mtcnn",
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
        
        regione = volto.get("region",{})
        genere = volto.get("dominant_gender","")
        emozione = volto.get("dominant_emotion","")
        eta = int(volto.get("age",0))

        return {
            "eta": eta,
            "genere": GENERE_ITA.get(genere),
            "emozione": EMOZIONI_ITA.get(emozione),
            "regione": regione
        }
    except Exception as e:
        print(f"[DEBUG] Errore: {e}")
        return None
    
    finally:
        del frame