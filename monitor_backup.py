import os
import subprocess
import datetime
import shutil

# --- CONFIGURAZIONE ---
 SOGLIA_FILE = 5  # Numero di file modificati per far scattare il backup incrementale
REPO_LOCALE = r"C:\Percorso\Della\Tua\Cartella\Locale"  # Inserisci il percorso del tuo progetto
DIR_BACKUP_INCREMENTALE = r"C:\Percorso\GoogleDrive\Snapshot_Incrementali"

def conta_file_modificati():
    """Esegue git status --porcelain per contare le modifiche non committate."""
    try:
        # Eseguiamo il comando Git nella cartella del repository
        risultato = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_LOCALE,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Dividiamo l'output per righe e rimuoviamo quelle vuote
        righe = [r for r in risultato.stdout.splitlines() if r.strip()]
        return len(righe), righe
        
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di Git: {e}")
        return 0, []

def esegui_backup_incrementale(lista_file):
    """Crea una cartella datata e copia solo i file modificati mantenendo la struttura."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    cartella_destinazione = os.path.join(DIR_BACKUP_INCREMENTALE, f"Snapshot_{timestamp}")
    
    print(f"\n[BACKUP] Creazione snapshot incrementale in: {cartella_destinazione}")
    os.makedirs(cartella_destinazione, exist_ok=True)
    
    for riga in lista_file:
        # git status --porcelain restituisce "Stato Percorso/File.est" (es. 'M path/to/file.txt')
        # Prendiamo solo il percorso del file escludendo i primi 3 caratteri di stato
        rel_path = riga[3:].strip('" ') 
        src_path = os.path.join(REPO_LOCALE, rel_path)
        dst_path = os.path.join(cartella_destinazione, rel_path)
        
        if os.path.exists(src_path) and os.path.isfile(src_path):
            # Crea le sottocartelle necessarie nella destinazione
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f" -> Copiato: {rel_path}")

    # Copiamo anche la cartella .git nascosta (opzionale, utile per mantenere lo stato)
    # Per una maggiore leggerezza incrementale, in questa fase copiamo solo i file modificati.

def main():
    print("Controllo dello stato del repository locale...")
    num_modifiche, righe_modificate = conta_file_modificati()
    
    print(f"File rilevati da ribaltamento: {num_modifiche} (Soglia impostata: {SOGLIA_FILE})")
    
    if num_modifiche >= SOGLIA_FILE:
        print("Soglia superata! Avvio del backup incrementale...")
        esegui_backup_incrementale(righe_modificate)
        print("[FINE] Backup completato con successo.")
    else:
        print("Modifiche inferiori alla soglia. Nessun backup necessario per ora.")

if __name__ == "__main__":
    main()