import pickle
record_list = []
total_accuracy = 0
try:
    with open("training_data.pkl","rb") as file:
        while True:
            try:
                record = pickle.load(file)
                total_accuracy += record["accuratezza"]
                record_list.append(record)
            except EOFError:
                break
except FileNotFoundError:
    print("Il file non è stato trovato")
    exit()

print(record_list)
print(f"Con {len(record_list)} esecuzioni l'accuratezza media è {total_accuracy/len(record_list)}")