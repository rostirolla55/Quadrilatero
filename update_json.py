import json
import sys
import os

def update_json_file():
    """
    Legge i parametri dalla riga di comando per aggiornare un file JSON.
    Uso: python update_json.py <json_path> <target_key> <text_source_path>
    """
    # 1. Verifica che i parametri siano stati forniti
    if len(sys.argv) != 4:
        print("Errore: Uso non corretto.")
        print("Sintassi: python update_json.py <percorso_json> <chiave_target> <percorso_testo>")
        sys.exit(1)

    # 2. Assegna i parametri
    json_path = sys.argv[1]
    target_key = sys.argv[2]
    text_source_path = sys.argv[3]

    if not os.path.exists(json_path):
        print(f"Errore: File JSON non trovato: {json_path}")
        sys.exit(1)

    if not os.path.exists(text_source_path):
        print(f"Errore: File di testo sorgente non trovato: {text_source_path}")
        sys.exit(1)

    try:
        # 3. Legge il contenuto del file di testo
        with open(text_source_path, 'r', encoding='utf-8') as f:
            testo_sorgente = f.read()

        # 4. Applica l'Escape CRITICO per le virgolette doppie (")
        # Sostituisce " con \"
        testo_escaped = testo_sorgente.replace('"', '\\"')
        
        # Rimuove newline in eccesso o caratteri di ritorno a capo comuni da file HTML puliti
        testo_escaped = testo_escaped.replace('\n', ' ').replace('\r', '').strip()

        # 5. Carica e aggiorna il file JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 6. Aggiorna la chiave target (la chiave viene creata se non esiste)
        # La chiave potrebbe essere nested (es. 'pioggia3.mainText1')
        keys = target_key.split('.')
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = testo_escaped
        print(f"✅ SUCCESS: Chiave '{target_key}' aggiornata in {json_path}")

        # 7. Scrive il JSON aggiornato
        with open(json_path, 'w', encoding='utf-8') as f:
            # Usa indent=4 per leggibilità, ensure_ascii=False per caratteri accentati
            json.dump(data, f, indent=4, ensure_ascii=False)

    except json.JSONDecodeError:
        print(f"ERRORE: Impossibile decodificare il JSON. Controllare la sintassi del file {json_path}.")
        sys.exit(1)
    except Exception as e:
        print(f"ERRORE inatteso: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_json_file()