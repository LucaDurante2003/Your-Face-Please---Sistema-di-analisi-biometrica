import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import pickle
from datetime import datetime

# Fase di configurazione: come si deve organizzare la RAM
path_dataset = "Dataset_Test" # Percorso dove si trova la cartella
img_size = (224, 224) # Dimensione obbligatoria per MobileNetV2
batch_size = 10       # Carichiamo 10 immagini alla volta in maniera tale da non sovraccaricare la RAM

# Fase di caricamento dei dati: ordina e assegna una etichetta alle cartelle nel dataset
dataset = tf.keras.utils.image_dataset_from_directory(
    path_dataset,
    image_size=img_size,
    batch_size=batch_size,
    shuffle=True # Mischia le immagini per un test imparziale
)

class_names = dataset.class_names
num_classes = len(class_names)
print(f"\nClassi rilevate ({num_classes}): {class_names}")

# Fase di normalizzazione: le immagini digitali hanno pixel con valori da 0 a 255 ma MobileNetV2 lavora con numeri fra -1 e +1
dataset_proc = dataset.map(lambda x, y: (preprocess_input(x), y))

# Fase di costruzione del modello: l'algoritmo viene scaricato e si rimuove l'ultimo strato che va sostituito con la nuova testa non ancora addestrata sui capelli
print("\nScaricamento e assemblaggio di MobileNetV2...")
base_model = MobileNetV2(
    input_shape=(224, 224, 3), 
    include_top=False, # Rimozione dell'ultimo strato
    weights='imagenet' # Algoritmo pre-addestrato
)

# La rete base viene congelata
base_model.trainable = False 

# Viene creata e aggiunta la nuova testa
inputs = tf.keras.Input(shape=(224, 224, 3))
x = base_model(inputs, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)

model = tf.keras.Model(inputs, outputs)

# Il modello viene compilato
model.compile(
    optimizer='adam', 
    loss='sparse_categorical_crossentropy', # formula matematica che misura quanto si sta sbagliando
    metrics=['accuracy']
)

# Fase di valutazione dell'accuratezza
print("\nInizio calcolo dell'accuratezza sulle 300 immagini")
loss, accuracy = model.evaluate(dataset_proc)
print("\n" + "="*40)
print(" RISULTATO DEL TEST")
print("="*40)
accuracy_percentage = round(accuracy * 100,2)
print(f"Accuratezza Iniziale: {accuracy_percentage}%")
print("="*40)

# Essendo 6 cartelle, se il modello non addestrato ha un'accuratezza intorno aL 17%, ciò viene considerato positivo poichè vuol dire
# che tira ad indovinare (1 su 6) e quindi rispetta le leggi della statistica

execution_date = datetime.now()

pretraining_data = {"data esecuzione":execution_date.strftime("%d/%m/%Y %H:%M:%S"),"accuratezza": accuracy_percentage}

with open("pre-training_data.pkl","ab") as file:
    pickle.dump(pretraining_data,file)