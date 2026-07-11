import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import pickle
from datetime import datetime

# Fase di configurazione: come si deve organizzare la RAM
path_dataset = "Dataset_Test" # Percorso dove si trova la cartella
img_size = (224, 224) # Dimensione obbligatoria per MobileNetV2
batch_size = 10 # Carichiamo 10 immagini alla volta in maniera tale da non sovraccaricare la RAM
epoche_fase_1 = 5 # Quante volte la rete vedrà tutto il dataset per addestrare la nuova testa (fase di addestramento)
epoche_fase_2 = 5 # Quante volte lo vedrà per riallineare la conoscenza del corpo a quella della testa (fase di fine-tuning)


# Fase di preparazione dei dati: l'80% delle immagini viene usata per il training mentre il restante 20% per testare l'accuratezza del modello dopo il training
train_ds = tf.keras.utils.image_dataset_from_directory(
    path_dataset,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=img_size,
    batch_size=batch_size
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    path_dataset,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=img_size,
    batch_size=batch_size
)

num_classes = len(train_ds.class_names)
print(f"Classi in addestramento: {train_ds.class_names}")

# Fase di normalizzazione: le immagini digitali hanno pixel con valori da 0 a 255 ma MobileNetV2 lavora con numeri fra -1 e +1
train_ds = train_ds.map(lambda x, y: (preprocess_input(x), y))
val_ds = val_ds.map(lambda x, y: (preprocess_input(x), y))

# Fase di costruzione del modello: l'algoritmo viene scaricato e si rimuove l'ultimo strato che va sostituito con la nuova testa non ancora addestrata sui capelli
base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')

# La rete base viene congelata
base_model.trainable = False 

# Viene creata e aggiunta la nuova testa
inputs = tf.keras.Input(shape=(224, 224, 3))
x = base_model(inputs, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)

# Il nuovo classificatore a 6 classi
outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)

model = tf.keras.Model(inputs, outputs)

# Fase 1 dell' addestramento della nuova testa sull'80% del dataset

# Viene usato un learning rate standard
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Prima fase di addestramento
storia_fase_1 = model.fit(train_ds, epochs=epoche_fase_1, validation_data=val_ds)


# Fase di fine-tuning: si scongela il corpo e gli si da un basso learning rate per allineare le sue conoscenze a quelle della nuova testa addestrata

# Il corpo viene scongelato
base_model.trainable = True

# I primi 100 strati (quelli che riconoscono le geometrie base) vengono ricongelati ma vengono scongelati solo gli strati dal 100 in poi , per fargli imparare la specificità dei capelli
for layer in base_model.layers[:100]:
    layer.trainable = False

# Il modello viene ricompilato con un learning rate molto basso, in maniera tale da non sconvolgere le conoscenze pregresse del modello
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Fase 2 dell' addestramento in cui si testa la nuova accuratezza del modello sul 20% del dataset
storia_fase_2 = model.fit(
    train_ds, 
    epochs=epoche_fase_1 + epoche_fase_2, 
    initial_epoch=storia_fase_1.epoch[-1], # Riparte dall'epoca 5
    validation_data=val_ds
)

# Fase di valutazione dell'accuratezza
print("\n" + "="*50)
print(" VALUTAZIONE FINALE SUL VALIDATION SET")
print("="*50)
loss, accuracy = model.evaluate(val_ds)
accuracy_percentage = round(accuracy * 100,2)
print(f"Accuratezza Definitiva: {accuracy_percentage}%")

# Se la nuova accuratezza si discosta di molto da quella pre-training, allora vuol dire che il modello risponde bene ed ha un corpo ben allenato
# per riconoscere la geometria base e su cui vanno create ed allenate nuove teste che servono per l'obiettivo del progetto

execution_date = datetime.now()

training_data = {"data esecuzione":execution_date.strftime("%d/%m/%Y %H:%M:%S"),"accuratezza": accuracy_percentage}

with open("training_data.pkl","ab") as file:
    pickle.dump(training_data,file)
