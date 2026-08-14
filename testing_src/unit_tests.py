"""
    Modulo per testare l'accuratezza delle singole funzioni del modulo engine/color_recognition.py
"""

import os
import sys
import unittest
import numpy as np

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.append(src_path)

from engine.color_recognition import (
    classifica_colore_occhi,
    classifica_colore_capelli,
    classifica_colore_pelle,
    ritaglio_roi,
    colore_dominante_hsv,
    estrai_roi_occhi,
    estrai_roi_capelli,
    estrai_roi_pelle,
)

class TestClassificaColoreOcchi(unittest.TestCase):
    """
        Classe che testa ogni ramo della funzione classifica_colore_occhi(h, s, v)
    """

    def test_nero_marrone_molto_scuro(self):
        """v < 50 → Nero / Marrone molto scuro"""
        self.assertEqual(classifica_colore_occhi(0, 100, 30), "Nero / Marrone molto scuro")

    def test_grigio(self):
        """v >= 50 e s < 30 → Grigio"""
        self.assertEqual(classifica_colore_occhi(50, 20, 100), "Grigio")

    def test_azzurro(self):
        """90 <= h <= 130, v > 150 → Azzurro"""
        self.assertEqual(classifica_colore_occhi(110, 80, 180), "Azzurro")

    def test_blu(self):
        """90 <= h <= 130, v <= 150 → Blu"""
        self.assertEqual(classifica_colore_occhi(100, 80, 120), "Blu")

    def test_verde_grigio(self):
        """35 <= h <= 85, s < 80 → Verde-Grigio"""
        self.assertEqual(classifica_colore_occhi(60, 50, 100), "Verde-Grigio")

    def test_verde(self):
        """35 <= h <= 85, s >= 80 → Verde"""
        self.assertEqual(classifica_colore_occhi(60, 120, 100), "Verde")

    def test_ambra_nocciola(self):
        """15 <= h <= 35, v > 150 → Ambra / Nocciola"""
        self.assertEqual(classifica_colore_occhi(25, 80, 180), "Ambra / Nocciola")

    def test_nocciola(self):
        """15 <= h <= 35, v <= 150 → Nocciola"""
        self.assertEqual(classifica_colore_occhi(25, 80, 100), "Nocciola")

    def test_marrone_chiaro(self):
        """(h < 15 or h > 160), s > 40, v > 130 → Marrone chiaro"""
        self.assertEqual(classifica_colore_occhi(10, 60, 150), "Marrone chiaro")

    def test_marrone_chiaro_hue_alto(self):
        """Stesso ramo ma con h > 160"""
        self.assertEqual(classifica_colore_occhi(170, 60, 150), "Marrone chiaro")

    def test_marrone_scuro(self):
        """(h < 15 or h > 160), s > 40, v <= 130 → Marrone scuro"""
        self.assertEqual(classifica_colore_occhi(10, 60, 80), "Marrone scuro")

    def test_marrone(self):
        """Nessun ramo precedente → Marrone"""
        self.assertEqual(classifica_colore_occhi(140, 35, 100), "Marrone")

class TestClassificaColoreCapelli(unittest.TestCase):
    """
        Classe che testa ogni ramo della funzione classifica_colore_capelli(h, s, v)
    """

    def test_nero(self):
        """v < 40 → Nero"""
        self.assertEqual(classifica_colore_capelli(0, 50, 20), "Nero")

    def test_bianco_grigio(self):
        """s < 25 e v > 180 → Bianco / Grigio"""
        self.assertEqual(classifica_colore_capelli(0, 10, 220), "Bianco / Grigio")

    def test_grigio(self):
        """s < 25 e v <= 180 → Grigio"""
        self.assertEqual(classifica_colore_capelli(0, 10, 150), "Grigio")

    def test_biondo_dorato(self):
        """15 <= h <= 35, v > 150, s > 100 → Biondo dorato"""
        self.assertEqual(classifica_colore_capelli(25, 120, 200), "Biondo dorato")

    def test_biondo_chiaro(self):
        """15 <= h <= 35, v > 150, s <= 100 → Biondo chiaro"""
        self.assertEqual(classifica_colore_capelli(25, 80, 200), "Biondo chiaro")

    def test_rosso_ramato(self):
        """(h < 15 or h > 160), s > 80, v > 130 → Rosso / Ramato"""
        self.assertEqual(classifica_colore_capelli(5, 100, 160), "Rosso / Ramato")

    def test_rosso_ramato_hue_alto(self):
        """Stesso ramo ma con h > 160"""
        self.assertEqual(classifica_colore_capelli(170, 100, 160), "Rosso / Ramato")

    def test_rosso_scuro(self):
        """(h < 15 or h > 160), s > 80, v <= 130 → Rosso scuro"""
        self.assertEqual(classifica_colore_capelli(5, 100, 100), "Rosso scuro")

    def test_castano_chiaro(self):
        """h < 25, s > 30, v > 120 → Castano chiaro"""
        self.assertEqual(classifica_colore_capelli(20, 50, 140), "Castano chiaro")

    def test_castano_scuro(self):
        """h < 25, s > 30, v <= 120 → Castano scuro"""
        self.assertEqual(classifica_colore_capelli(20, 50, 80), "Castano scuro")

    def test_castano(self):
        """Nessun ramo precedente → Castano"""
        self.assertEqual(classifica_colore_capelli(40, 28, 100), "Castano")

class TestClassificaColorePelle(unittest.TestCase):
    """
        Classe che testa ogni ramo della funzione classifica_colore_pelle(h, s, v)
    """

    def test_molto_chiaro(self):
        """v > 200, s < 60 → Molto chiaro"""
        self.assertEqual(classifica_colore_pelle(15, 40, 230), "Molto chiaro")

    def test_chiaro(self):
        """v > 170 (ma non molto chiaro perché s >= 60) → Chiaro"""
        self.assertEqual(classifica_colore_pelle(15, 80, 190), "Chiaro")

    def test_medio(self):
        """v > 130 → Medio"""
        self.assertEqual(classifica_colore_pelle(15, 80, 150), "Medio")

    def test_olivastro(self):
        """v > 80 → Olivastro"""
        self.assertEqual(classifica_colore_pelle(15, 80, 100), "Olivastro")

    def test_scuro(self):
        """v > 50 → Scuro"""
        self.assertEqual(classifica_colore_pelle(15, 80, 60), "Scuro")

    def test_molto_scuro(self):
        """v <= 50 → Molto scuro"""
        self.assertEqual(classifica_colore_pelle(15, 80, 30), "Molto scuro")


class TestRitaglioRoi(unittest.TestCase):
    """
        Classe che testa la funzione ritaglio_roi con frame sintetici (numpy array)
    """

    def setUp(self):
        """Crea un frame di test 100x100 con 3 canali (BGR)"""
        self.frame = np.zeros((100, 100, 3), dtype=np.uint8)

    def test_ritaglio_centro(self):
        """Ritaglio normale al centro del frame"""
        roi = ritaglio_roi(self.frame, 50, 50, 20, 20)
        self.assertIsNotNone(roi)
        self.assertEqual(roi.shape[0], 40)
        self.assertEqual(roi.shape[1], 40)

    def test_ritaglio_bordo(self):
        """Ritaglio vicino al bordo: le coordinate vengono fissate a 0"""
        roi = ritaglio_roi(self.frame, 5, 5, 20, 20)
        self.assertIsNotNone(roi)
        self.assertEqual(roi.shape[1], 25)
        self.assertEqual(roi.shape[0], 25)

    def test_ritaglio_troppo_piccolo(self):
        """ROI troppo piccola (< 5px) → restituisce None"""
        roi = ritaglio_roi(self.frame, 50, 50, 2, 2)
        self.assertIsNone(roi)

    def test_ritaglio_bordo_estremo(self):
        """Ritaglio con centro all'angolo in basso a destra"""
        roi = ritaglio_roi(self.frame, 98, 98, 20, 20)
        self.assertIsNotNone(roi)
        self.assertEqual(roi.shape[1], 22)

class TestColoreDominanteHsv(unittest.TestCase):
    """
        Classe che testa la funzione colore_dominante_hsv con ROI sintetiche
    """

    def test_input_none(self):
        """Input None → restituisce None"""
        self.assertIsNone(colore_dominante_hsv(None))

    def test_input_vuoto(self):
        """Array vuoto → restituisce None"""
        roi_vuota = np.array([], dtype=np.uint8).reshape(0, 0, 3)
        self.assertIsNone(colore_dominante_hsv(roi_vuota))

    def test_pixel_insufficienti(self):
        """Meno pixel dei cluster richiesti → restituisce None"""
        roi_piccola = np.zeros((1, 2, 3), dtype=np.uint8)
        self.assertIsNone(colore_dominante_hsv(roi_piccola))

    def test_colore_uniforme(self):
        """ROI di colore uniforme blu puro BGR(255,0,0) → centroide atteso ~(120, 255, 255) in HSV"""
        roi_blu = np.full((20, 20, 3), [255, 0, 0], dtype=np.uint8)
        risultato = colore_dominante_hsv(roi_blu)
        self.assertIsNotNone(risultato)
        h, s, v = risultato
        self.assertEqual(h, 120)
        self.assertEqual(s, 255)
        self.assertEqual(v, 255)

class TestEstraiRoiOcchi(unittest.TestCase):
    """
        Classe che testa la funzione estrai_roi_occhi con landmark simulati
    """

    def setUp(self):
        """Crea un frame di test 200x200"""
        self.frame = np.zeros((200, 200, 3), dtype=np.uint8)

    def test_entrambi_gli_occhi(self):
        """Landmark con entrambi gli occhi → restituisce ROI combinata"""
        landmark = {"left_eye": [60, 80], "right_eye": [140, 80]}
        roi = estrai_roi_occhi(self.frame, landmark)
        self.assertIsNotNone(roi)

    def test_un_solo_occhio(self):
        """Landmark con un solo occhio → restituisce ROI di quell'occhio"""
        landmark = {"left_eye": [60, 80]}
        roi = estrai_roi_occhi(self.frame, landmark)
        self.assertIsNotNone(roi)

    def test_nessun_occhio(self):
        """Landmark senza occhi → restituisce None"""
        landmark = {"nose": [100, 100]}
        roi = estrai_roi_occhi(self.frame, landmark)
        self.assertIsNone(roi)

    def test_landmark_vuoto(self):
        """Landmark completamente vuoto → restituisce None"""
        roi = estrai_roi_occhi(self.frame, {})
        self.assertIsNone(roi)

class TestEstraiRoiCapelli(unittest.TestCase):
    """
        Classe che testa la funzione estrai_roi_capelli con regioni simulate
    """

    def setUp(self):
        """Crea un frame di test 400x400"""
        self.frame = np.zeros((400, 400, 3), dtype=np.uint8)

    def test_regione_valida(self):
        """Regione del volto sufficientemente grande → restituisce ROI dei capelli"""
        regione = {"x": 100, "y": 100, "w": 200, "h": 200}
        landmark = {}
        roi = estrai_roi_capelli(self.frame, landmark, regione)
        self.assertIsNotNone(roi)

    def test_regione_troppo_piccola(self):
        """Regione troppo piccola → restituisce None"""
        regione = {"x": 100, "y": 10, "w": 20, "h": 10}
        landmark = {}
        roi = estrai_roi_capelli(self.frame, landmark, regione)
        self.assertIsNone(roi)

    def test_regione_bordo_superiore(self):
        """Volto in cima al frame (y=0) → area capelli fissata, restituisce None"""
        regione = {"x": 100, "y": 0, "w": 200, "h": 200}
        landmark = {}
        roi = estrai_roi_capelli(self.frame, landmark, regione)
        self.assertIsNone(roi)

class TestEstraiRoiPelle(unittest.TestCase):
    """
        Classe che testa la funzione estrai_roi_pelle con landmark simulati
    """

    def setUp(self):
        """Crea un frame di test 400x400"""
        self.frame = np.zeros((400, 400, 3), dtype=np.uint8)

    def test_landmark_completi(self):
        """Landmark con naso e entrambi gli occhi → restituisce ROI pelle"""
        landmark = {
            "nose": [200, 200],
            "left_eye": [150, 170],
            "right_eye": [250, 170],
        }
        roi = estrai_roi_pelle(self.frame, landmark)
        self.assertIsNotNone(roi)

    def test_manca_naso(self):
        """Landmark senza naso → restituisce None"""
        landmark = {"left_eye": [150, 170], "right_eye": [250, 170]}
        roi = estrai_roi_pelle(self.frame, landmark)
        self.assertIsNone(roi)

    def test_manca_occhio_sinistro(self):
        """Landmark senza occhio sinistro → restituisce None"""
        landmark = {"nose": [200, 200], "right_eye": [250, 170]}
        roi = estrai_roi_pelle(self.frame, landmark)
        self.assertIsNone(roi)

    def test_manca_occhio_destro(self):
        """Landmark senza occhio destro → restituisce None"""
        landmark = {"nose": [200, 200], "left_eye": [150, 170]}
        roi = estrai_roi_pelle(self.frame, landmark)
        self.assertIsNone(roi)

    def test_landmark_vuoto(self):
        """Landmark completamente vuoto → restituisce None"""
        roi = estrai_roi_pelle(self.frame, {})
        self.assertIsNone(roi)

if __name__ == "__main__":
    unittest.main()