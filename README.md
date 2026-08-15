# Your Face, Please - Sistema di analisi biometrica

## Descrizione

Applicazione desktop nativa in Python che cattura il flusso video da webcam in tempo reale ed esegue una pipeline di analisi biometrica sul volto inquadrato per determinare:
- **Età**
-  **Genere**
- **Espressione facciale**
- **Colore degli occhi**
-  **Colore dei capelli**
-  **Colore della pelle**

Le prime tre informazioni vengono rilevate mediante l'utilizzo del Deep Learning, mentre le restanti tramite tecniche di Computer Vision classica (clustering geometrico).

## Stack tecnologico
Di seguito vengono illustrate le tecnologie utilizzate:
- **Linguaggio**: Python 3.10.20
-  **Interfaccia grafica (GUI)**: PySide6 (Qt for Python)
- **Acquisizione e manipolazione video**: OpenCV
- **Inferenza semantica**: DeepFace (con backend di rilevamento landmark nativo RetinaFace)
-  **Analisi cromatica**: NumPy e Cv2 (algoritmo K-means in spazio colore HSV)

## Struttura della repository
Da aggiungere

## Rispetto della Privacy by Design (GDPR Art. 25)

L'applicazione rispetta la *Data Minimization*:
- L'elaborazione avviene esclusivamente in Edge Computing (RAM locale)
- I buffer dei frame video inviati ai modelli IA vengono distrutti esplicitamente dal ciclo di memoria dopo l'estrazione del metadato
- Nessuna immagine, log identificativo o stream video viene salvato su disco locale o inviato a server cloud

## Dipendenze

Si consiglia di creare un ambiente virtuale (es: Conda) per eseguire un'installazione pulita in un ambiente isolato delle librerie necessarie affinché l'applicazione svolga la sua corretta funzione
```
conda create --name nome_env python=3.10.20 -y
conda activate nome_env
```
Spostarsi poi nella cartella principale dell'applicazione ed eseguire il seguente comando per installare le librerie:
```
pip install -r requirements.txt
```
## Come eseguire l'applicazione

Attivare l'ambiente Conda precedentemente creato ed inizializzato
```
conda activate nome_env
```
Partendo dalla cartella principale dell'applicazione, recarsi nella cartella *src* ed eseguire il file *main.py*
```
cd src
python main.py
```
## Come testare l'applicazione
Da aggiungere
