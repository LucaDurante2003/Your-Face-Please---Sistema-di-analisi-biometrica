import subprocess
import sys
import time

scripts = ["pre-training.py","training.py"]

start = time.time()
for script in scripts:
    executions = 0
    while (executions < 50):
        try:
            subprocess.run([sys.executable,script],check=True)
            executions +=1
        except subprocess.CalledProcessError as e:
            print(f"Errore durante l'esecuzione dello script {script}: {e}")
            exit()
end = time.time()

print(f"Tutti gli script sono stati eseguiti e terminati con successo in {round(end - start,None)} secondi")