# Your Face, Please - Sistema di analisi biometrica

## Descrizione

Applicazione desktop nativa in Python che cattura il flusso video da webcam in tempo reale ed esegue una pipeline di analisi biometrica sul volto inquadrato per determinare:
- **Età**
- **Genere**
- **Espressione facciale**
- **Colore degli occhi**
- **Colore dei capelli**
- **Colore della pelle**

Le prime tre informazioni vengono rilevate mediante l'utilizzo del Deep Learning, mentre le restanti tramite tecniche di Computer Vision classica (clustering geometrico).

## Stack tecnologico
Di seguito vengono illustrate le tecnologie utilizzate:
- **Linguaggio**: Python 3.10.20
- **Interfaccia grafica (GUI)**: PySide6 (Qt for Python)
- **Acquisizione e manipolazione video**: OpenCV
- **Inferenza semantica**: DeepFace (con backend di rilevamento landmark nativo RetinaFace)
- **Analisi cromatica**: NumPy e Cv2 (algoritmo K-means in spazio colore HSV)

## Struttura della repository
```
├── docs/                                  # Documentazione e paper di riferimento
├── src/                                   # Codice sorgente dell'applicazione
│   ├── engine/                            # Logica di analisi biometrica
│   │   ├── __init__.py
│   │   ├── color_recognition.py           # Riconoscimento cromatico (occhi, capelli, pelle)
│   │   └── face_recognition.py            # Riconoscimento facciale (età, genere, espressione)
│   ├── threads/                           # Gestione dei thread
│   │   ├── __init__.py
│   │   ├── video_thread.py                # Thread di acquisizione video da webcam
│   │   └── worker_thread.py               # Thread di elaborazione dei frame
│   ├── ui/                                # Interfaccia grafica
│   │   ├── fonts/                         # Font personalizzati
│   │   ├── img/                           # Risorse grafiche
│   │   ├── styles/                        # Fogli di stile Qt (QSS)
│   │   │   ├── main_window.qss
│   │   │   └── start_window.qss
│   │   ├── __init__.py
│   │   ├── main_window.py                 # Finestra principale dell'applicazione
│   │   └── start_window.py                # Finestra iniziale dell'applicazione
│   ├── __init__.py
│   └── main.py                            # Entry point dell'applicazione
├── testing_src/                           # Test e validazione
│   ├── dataset/                           # Dataset per i test di accuratezza
│   │   ├── img_dataset/                   # Immagini di test
│   │   └── dataset.json                   # Ground truth del dataset
│   ├── results/                           # Generata automaticamente da accuracy_test.py
│   ├── accuracy_test.py                   # Test di accuratezza dei modelli
│   └── unit_tests.py                      # Test unitari (color_recognition)
├── .gitignore
├── README.md
└── requirements.txt                       # Dipendenze Python
```

## Rispetto della Privacy by Design (GDPR Art. 25)

L'applicazione rispetta la *Data Minimization*:
- L'elaborazione avviene esclusivamente in *Edge Computing* (RAM locale)
- I buffer dei frame video inviati ai modelli IA vengono distrutti esplicitamente dal ciclo di memoria dopo l'estrazione del metadato
- Nessuna immagine, log identificativo o stream video viene salvato su disco locale o inviato a server cloud

## Installazione

Si consiglia di creare un ambiente virtuale (es: Conda) per eseguire un'installazione pulita, in un ambiente isolato, delle librerie necessarie affinché l'applicazione svolga la sua corretta funzione.

Creare e attivare l'ambiente:
```
conda create --name nome_env python=3.10.20 -y
conda activate nome_env
```
Spostarsi poi nella cartella principale dell'applicazione ed installare le dipendenze:
```
pip install -r requirements.txt
```

> **Nota**: per tutti i comandi successivi si assume che l'ambiente Conda sia già attivo (`conda activate nome_env`).

## Come eseguire l'applicazione

Partendo dalla cartella principale dell'applicazione, recarsi nella cartella *src* ed eseguire il file *main.py*:
```
cd src
python main.py
```

## Come testare l'applicazione

Partendo dalla cartella principale dell'applicazione, recarsi nella cartella *testing_src* ed eseguire il file *accuracy_test.py*:
```
cd testing_src
python accuracy_test.py
```
Una volta conclusa l'esecuzione dello script, verrà creata automaticamente la cartella *results* contenente i risultati sotto forma di file *csv*.

Se invece si volessero eseguire i test unitari sulle funzioni del file *color_recognition.py*, rimanendo nella cartella *testing_src*, eseguire il file *unit_tests.py*:
```
python unit_tests.py
```
