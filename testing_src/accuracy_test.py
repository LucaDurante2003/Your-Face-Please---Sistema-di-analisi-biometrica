"""
    Modulo per testare l'accuratezza dell'applicazione su un dataset di 50 immagini
"""

import os
import sys
import json
import csv
import cv2
import logging

logger = logging.getLogger(__name__)

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.append(src_path)

from engine import analizza_volto, analizza_colori

def main():
    """
        Funzione che genera un file csv con i risultati del test
    """

    cartella_testing = os.path.dirname(__file__)
    cartella_dataset = os.path.join(cartella_testing, "dataset")
    cartella_risultati = os.path.join(cartella_testing, "results")
    cartella_immagini = os.path.join(cartella_dataset, "img_dataset")
    path_json_input = os.path.join(cartella_dataset, "dataset.json")
    path_csv_output = os.path.join(cartella_risultati, "test_results.csv")

    if os.path.exists(path_json_input):
        with open(path_json_input, "r", encoding="utf-8") as f:
            dataset_json = json.load(f)
    else:
        logger.error("Errore: problema nel path del file dataset.json: %s", path_json_input)
        return None

    totale_immagini = len(dataset_json)
    volti_rilevati = 0

    corretti = {
        "genere": 0,
        "emozione": 0,
        "occhi": 0,
        "capelli": 0,
        "pelle": 0,
        "eta_range_10_anni": 0
    }
    
    somma_errori_eta = 0

    for nome_img, dati_reali in dataset_json.items():
        path_img = os.path.join(cartella_immagini, nome_img)
        
        if not os.path.exists(path_img):
            continue

        frame = cv2.imread(path_img)
        
        risultati_volto = analizza_volto(frame)
        
        if risultati_volto is None:
            continue
            
        volti_rilevati += 1
        
        landmarks = risultati_volto.get("landmarks")
        regione = risultati_volto.get("regione")
        
        if landmarks and regione:
            colori = analizza_colori(frame, landmarks, regione)
            risultati_volto.update(colori)
        
        if risultati_volto.get("genere") == dati_reali.get("genere"):
            corretti["genere"] += 1
            
        if risultati_volto.get("emozione") == dati_reali.get("emozione"):
            corretti["emozione"] += 1
            
        if risultati_volto.get("colore_occhi") == dati_reali.get("occhi"):
            corretti["occhi"] += 1
            
        if risultati_volto.get("colore_capelli") == dati_reali.get("capelli"):
            corretti["capelli"] += 1
            
        if risultati_volto.get("colore_pelle") == dati_reali.get("pelle"):
            corretti["pelle"] += 1

        eta_stimata = risultati_volto.get("eta", 0)
        eta_reale = dati_reali.get("eta", 0)
        
        errore_assoluto = abs(eta_stimata - eta_reale)
        somma_errori_eta += errore_assoluto
        
        if errore_assoluto <= 10:
            corretti["eta_range_10_anni"] += 1

    
    if volti_rilevati > 0:
        base_calcolo = volti_rilevati
    else:
        base_calcolo = 1

    acc_volti = (volti_rilevati / totale_immagini) * 100
    acc_genere = (corretti["genere"] / base_calcolo) * 100
    acc_emozione = (corretti["emozione"] / base_calcolo) * 100
    acc_occhi = (corretti["occhi"] / base_calcolo) * 100
    acc_capelli = (corretti["capelli"] / base_calcolo) * 100
    acc_pelle = (corretti["pelle"] / base_calcolo) * 100
    acc_eta_range = (corretti["eta_range_10_anni"] / base_calcolo) * 100
    
    mae_eta = somma_errori_eta / base_calcolo

    if os.path.isdir(cartella_risultati):
        with open(path_csv_output, "w", newline="", encoding="utf-8") as file_csv:
            writer = csv.writer(file_csv, delimiter=";")
        
            writer.writerow(["Metrica", "Valore", "Dettagli"])
            writer.writerow(["Totale Immagini Dataset", totale_immagini, ""])
            writer.writerow(["Accuratezza Volti Rilevati", f"{acc_volti:.2f}%", f"{volti_rilevati} su {totale_immagini}"])
            writer.writerow([])
        
            writer.writerow(["Accuratezza Genere", f"{acc_genere:.2f}%", f"{corretti['genere']} su {volti_rilevati}"])
            writer.writerow(["Accuratezza Emozione", f"{acc_emozione:.2f}%", f"{corretti['emozione']} su {volti_rilevati}"])
            writer.writerow(["Accuratezza Colore Occhi", f"{acc_occhi:.2f}%", f"{corretti['occhi']} su {volti_rilevati}"])
            writer.writerow(["Accuratezza Colore Capelli", f"{acc_capelli:.2f}%", f"{corretti['capelli']} su {volti_rilevati}"])
            writer.writerow(["Accuratezza Colore Pelle", f"{acc_pelle:.2f}%", f"{corretti['pelle']} su {volti_rilevati}"])
            writer.writerow([])
        
            writer.writerow(["Accuratezza Età (Tolleranza ±10)", f"{acc_eta_range:.2f}%", f"{corretti['eta_range_10_anni']} su {volti_rilevati}"])
            writer.writerow(["Mean Absolute Error (MAE) Età", f"{mae_eta:.2f} anni", ""])
    else:
        logger.error("Errore: la cartella results non esiste: %s", cartella_risultati)
        return None

if __name__ == "__main__":
    main()