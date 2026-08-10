"""
    Modulo per il riconoscimento del colore degli occhi, della pelle e dei capelli
    tramite il ritaglio delle aree di interesse e l'applicazione dell'algoritmo di clustering K-Means
"""

import cv2
import numpy as np

def classifica_colore_occhi(h, s, v):
    """
        Funzione che classifica il colore degli occhi basandosi sui valori HSV del centroide dominante

        Args:
            h: componente Hue, ossia la tonalità
            s: componente Saturation, ossia la saturazione
            v: componente Value, ossia la luminosità
        
        Returns:
            str: stringa che descrive il colore degli occhi

    """

    if v < 50:
        return "Nero / Marrone molto scuro"
    
    if s < 30:
        return "Grigio"

    if 90 <= h <= 130:
        if v > 150:
            return "Azzurro"
        return "Blu"
    
    if 35 <= h <= 85:
        if s < 80:
            return "Verde-Grigio"
        return "Verde"
    
    if 15 <= h <= 35:
        if v > 150:
            return "Ambra / Nocciola"
        return "Nocciola"
    
    if (h < 15 or h > 160) and s > 40:
        if v > 130:
            return "Marrone chiaro"
        return "Marrone scuro"
    
    return "Marrone"

def classifica_colore_capelli(h , s, v):
    """
        Funzione che classifica il colore dei capelli basandosi sui valori HSV del centroide dominante

        Args:
            h: componente Hue, ossia la tonalità
            s: componente Saturation, ossia la saturazione
            v: componente Value, ossia la luminosità
        
        Returns:
            str: stringa che descrive il colore dei capelli

    """

    if v < 40:
        return "Nero"
    
    if s < 25:
        if v > 180:
            return "Bianco / Grigio"
        return "Grigio"
    
    if 15 <= h <= 35 and v > 150:
        if s > 100:
            return "Biondo dorato"
        return "Biondo chiaro"
    
    if (h < 15 or h > 160) and s > 80:
        if v > 130:
            return "Rosso / Ramato"
        return "Rosso scuro"
    
    if h < 25 and s > 30:
        if v > 120:
            return "Castano chiaro"
        return "Castano scuro"
    
    return "Castano"

def classifica_colore_pelle(h, s, v):
    """
        Funzione che classifica il colore della pelle basandosi sui valori HSV del centroide dominante

        Args:
            h: componente Hue, ossia la tonalità
            s: componente Saturation, ossia la saturazione
            v: componente Value, ossia la luminosità
        
        Returns:
            str: stringa che descrive il colore della pelle

    """

    if v > 200 and s < 60:
        return "Molto chiaro"
    
    if v > 170:
        return "Chiaro"
    
    if v > 130:
        return "Medio"
    
    if v > 80:
        return "Olivastro"
    
    if v > 50:
        return "Scuro"
    
    return "Molto scuro"

def ritaglio_roi(frame, centro_x, centro_y, raggio_x, raggio_y):
    """
        Funzione che ritaglia una regione rettangolare del frame centrata in un punto, gestendo i bordi
        per evitare di andare fuori range

        Args:
            frame: immagine BGR sottoforma di numpy array
            centro_x: coordinata x del centro della ROI
            centro_y: coordinata y del centro della ROI
            raggio_x: metà larghezza della ROI
            raggio_y: metà altezza della ROI
        
        Returns:
            numpy array: porzione di immagine ritagliata, oppure None se troppo piccola
    """

    altezza, larghezza = frame.shape[:2]

    x1 = max(0, centro_x - raggio_x)
    y1 = max(0, centro_y - raggio_y)
    x2 = min(larghezza, centro_x + raggio_x)
    y2 = min(altezza, centro_y + raggio_y)

    if (x2 - x1) < 5 or (y2 - y1) < 5:
        return None
    
    return frame[y1:y2, x1:x2]

def estrai_roi_occhi(frame, landmark):
    """
        Funzione che estrae la ROI degli occhi dai landmark facciali

        Args:
            frame: immagine BGR a risoluzione originale
            landmark: dict dei landmark facciali
        
        Returns:
            numpy array: ROI combinata di entrambi gli occhi, oppure None
    """
    
    roi_list = []
    for chiave in ("left_eye","right_eye"):
        punto = landmark.get(chiave)
        if punto is None:
            continue
        c_x, c_y = int(punto[0]), int(punto[1])
        roi = ritaglio_roi(frame, c_x, c_y, 15, 10)
        if roi is not None:
            roi_list.append(roi.reshape(-1, 3))
    
    if not roi_list:
        return None
    
    pixel_combinati = np.vstack(roi_list)
    if len(pixel_combinati) > 0:
        return pixel_combinati.reshape(-1, 1, 3)
    return None

def estrai_roi_capelli(frame, landmark, regione):
    """
        Funzione che estrae la ROI dei capelli dall'area sopra il riquadro che identifica il volto

        Args:
            frame: immagine BGR a risoluzione originale
            landmark: dict dei landmark facciali
            regione: riquadro che identifica il volto
        
        Returns:
            numpy array: ROI dei capelli, oppure None
    """
    
    altezza_frame, larghezza_frame = frame.shape[:2]
    x = regione["x"]
    y = regione["y"]
    w = regione["w"]
    altezza_roi = int(regione["h"] * 0.35)

    margine_laterale = int(w * 0.1)

    y1 = max(0, y - altezza_roi)
    y2 = max(0, y)
    x1 = max(0, x - margine_laterale)
    x2 = min(larghezza_frame, x + w + margine_laterale)

    if (x2 - x1) < 10 or (y2 - y1) < 10:
        return None
    
    roi_bgr = frame[y1:y2, x1:x2]
    roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)

    maschera_pelle = cv2.inRange(roi_hsv, np.array([0, 30, 80]), np.array([25, 170, 255]))
    maschera_blu = cv2.inRange(roi_hsv, np.array([90, 50, 50]), np.array([140, 255, 255]))
    maschera_verde = cv2.inRange(roi_hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
    maschera_escludi = maschera_pelle | maschera_blu | maschera_verde
    maschera_capelli = cv2.bitwise_not(maschera_escludi)
    pixel_capelli = roi_bgr[maschera_capelli > 0]
    
    if len(pixel_capelli) < 20:
        return None
    
    return pixel_capelli.reshape(-1, 1, 3)

def estrai_roi_pelle(frame, landmark):
    """
        Funzione che estrae la ROI della pelle dalle guance, che funge da riferimento

        Args:
            frame: immagine BGR a risoluzione originale
            landmark: dict dei landmark facciali
        
        Returns:
            numpy array: ROI della pelle delle guance, oppure None
    """
    
    naso = landmark.get("nose")
    occhio_sx = landmark.get("left_eye")
    occhio_dx = landmark.get("right_eye")

    if naso is None or occhio_sx is None or occhio_dx is None:
        return None
    
    distanza_occhi = abs(int(occhio_sx[0]) - int(occhio_dx[0]))
    raggio = max(10, distanza_occhi // 5)
    naso_x, naso_y = int(naso[0]), int(naso[1])

    offset_x = distanza_occhi // 3
    roi_sx = ritaglio_roi(frame, naso_x - offset_x, naso_y + raggio, raggio, raggio)
    roi_dx = ritaglio_roi(frame, naso_x + offset_x, naso_y + raggio, raggio, raggio)

    roi_list = []
    for roi in (roi_sx, roi_dx):
        if roi is not None:
            roi_list.append(roi.reshape(-1, 3))
    
    if not roi_list:
        return None
    
    pixel_combinati = np.vstack(roi_list)
    if len(pixel_combinati) > 0:
        return pixel_combinati.reshape(-1, 1, 3)
    return None

def colore_dominante_hsv(roi_bgr, n_clusters=3):
    """
        Funzione che applica l'algoritmo K-Means sulla ROI convertita in HSV per trovare il colore dominante, cioè il centroide del cluster più numeroso

        Args:
            roi_bgr: ROI in formato BGR
            n_clusters: numero di cluster per K-Means
        
        Returns:
            h, s, v: tupla con valori del colore dominante, oppure None
    """
    
    if roi_bgr is None or roi_bgr.size == 0:
        return None
    
    roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    matrice = roi_hsv.reshape(-1, 3).astype(np.float32)

    if len(matrice) < n_clusters:
        return None
    
    criteri = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, etichette, centri = cv2.kmeans(matrice, n_clusters, None, criteri, 5, cv2.KMEANS_PP_CENTERS)
    etichette_flat = etichette.flatten()
    valori_unici, conteggi = np.unique(etichette_flat, return_counts=True)
    indice_dominante = valori_unici[np.argmax(conteggi)]
    centroide = centri[indice_dominante]

    h, s, v = int(centroide[0]), int(centroide[1]), int(centroide[2])

    return h, s, v

def analizza_colori(frame, landmark, regione):
    """
        Funzione che trova il colore dominante per ogni zona d'interesse

        Args:
            frame: immagine BGR a risoluzione originale
            landmark: dict dei landmark facciali
            regione: riquadro che identifica il volto
        
        Returns:
            risultato: dict con i colori dominanti rilevati
    """
    
    risultati = {
        "colore_occhi": "Non rilevato",
        "colore_capelli": "Non rilevato",
        "colore_pelle": "Non rilevato",
    }

    roi_occhi = None
    roi_capelli = None
    roi_pelle = None

    try:
        roi_occhi = estrai_roi_occhi(frame, landmark)
        hsv_occhi = colore_dominante_hsv(roi_occhi)
        if hsv_occhi is not None:
            risultati["colore_occhi"] = classifica_colore_occhi(hsv_occhi[0], hsv_occhi[1], hsv_occhi[2])
    
        roi_capelli = estrai_roi_capelli(frame, landmark, regione)
        hsv_capelli = colore_dominante_hsv(roi_capelli)
        if hsv_capelli is not None:
            risultati["colore_capelli"] = classifica_colore_capelli(hsv_capelli[0], hsv_capelli[1], hsv_capelli[2])
    
        roi_pelle = estrai_roi_pelle(frame, landmark)
        hsv_pelle = colore_dominante_hsv(roi_pelle)
        if hsv_pelle is not None:
            risultati["colore_pelle"] = classifica_colore_pelle(hsv_pelle[0], hsv_pelle[1], hsv_pelle[2])
    
        return risultati
    
    finally:
        if roi_occhi is not None:
            roi_occhi.fill(0)
            del roi_occhi
        if roi_capelli is not None:
            roi_capelli.fill(0)
            del roi_capelli
        if roi_pelle is not None:
            roi_pelle.fill(0)
            del roi_pelle