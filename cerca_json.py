import csv
import glob
import json
import os
import sys


def cerca_chiave_json_csv(chiave_cercata, pattern_path, salta_vuoti=True):
    """Estrae una sotto-chiave (es. mainText, pageTitle, audioSource)

    da tutti i POI presenti nei file texts.json delle varie lingue,
    usando ';' come delimitatore CSV.
    """
    files_trovati = sorted(glob.glob(pattern_path, recursive=True))

    if not files_trovati:
        sys.stderr.write(f"Errore: nessun file trovato con '{pattern_path}'.\n")
        return

    chiave_lower = chiave_cercata.lower()
    trovato = False

    # Impostato delimiter=';' per compatibilità diretta con Excel
    writer = csv.writer(sys.stdout, delimiter=';', lineterminator='\n')
    writer.writerow(['lingua', 'poi', 'chiave', 'valore', 'file'])

    for file_path in files_trovati:
        # Ricava il codice lingua dal nome della cartella padre (es. 'it', 'en', 'es', 'fr')
        lingua = os.path.basename(os.path.dirname(file_path))

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                if not isinstance(data, dict):
                    continue

                # Scorre i POI di primo livello (es. "home", "santuariopioggia", ...)
                for poi, contenuti in data.items():
                    if not isinstance(contenuti, dict):
                        continue

                    # Cerca la chiave ignorando maiuscole/minuscole
                    for k, valore in contenuti.items():
                        if k.lower() == chiave_lower:
                            if isinstance(valore, (dict, list)):
                                valore_str = json.dumps(valore, ensure_ascii=False)
                            else:
                                valore_str = str(valore)

                            if salta_vuoti and valore_str.strip() == '':
                                continue

                            writer.writerow([
                                lingua,
                                poi,
                                k,
                                valore_str,
                                os.path.abspath(file_path),
                            ])
                            trovato = True
        except Exception as e:
            sys.stderr.write(f"Errore lettura {file_path}: {e}\n")
            continue

    if not trovato:
        sys.stderr.write(
            f"Attenzione: chiave '{chiave_cercata}' non trovata nei {len(files_trovati)} file analizzati.\n"
        )


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        cerca_chiave_json_csv(sys.argv[1], sys.argv[2])
    else:
        print('Uso: python cerca_json.py [chiave] [pattern_path_json]')