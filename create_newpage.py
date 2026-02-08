import json
import os

def generate_bat_from_config(target_page_id):
    config_file = "pois_config.json"
    template_file = "add_newpage.bat" # Usato come riferimento per i percorsi fissi
    
    if not os.path.exists(config_file):
        print(f"Errore: {config_file} non trovato.")
        return

    # 1. Caricamento dati dal JSON
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Cerca il blocco della pagina specifica
    page_data = next((p for p in data.get("pois", []) if p["id"] == target_page_id), None)
    
    if not page_data:
        print(f"Errore: Pagina '{target_page_id}' non trovata nel file di configurazione JSON.")
        return

    # 2. Definizione dei contenuti per il file .bat
    # Nota: I percorsi REPO_ROOT e UTILITIES sono estratti logicamente dal tuo template
    # ma rimangono costanti per la tua installazione locale.
    
    bat_content = f"""@echo off
ECHO =========================================================
ECHO AGGIUNTA NUOVA PAGINA: {page_data['id']}
ECHO =========================================================

:: --- CONFIGURAZIONE PAGINA GENERATA AUTOMATICAMENTE ---
SET "PAGE_ID={page_data['id']}"
SET "NAV_KEY_ID={page_data['nav_id']}"
SET "PAGE_TITLE_IT=Titolo per {page_data['id']}"
SET "LAT={page_data['lat']}"
SET "LON={page_data['lon']}"
SET "DISTANCE={page_data['threshold']}"
SET "REPO_ROOT=C:\\Users\\User\\Documents\\GitHub\\Quadrilatero"
SET "UTILITIES=%REPO_ROOT%\\Utilities"
:: ------------------------------------------------------

ECHO 1. Eseguo il backup dei file critici...
CALL "%UTILITIES%\\salvag.bat" "%REPO_ROOT%\\main.js"
CALL "%UTILITIES%\\salvag.bat" "%REPO_ROOT%\\data\\translations\\it\\texts.json"
CALL "%UTILITIES%\\salvag.bat" "%REPO_ROOT%\\data\\translations\\en\\texts.json"
CALL "%UTILITIES%\\salvag.bat" "%REPO_ROOT%\\data\\translations\\es\\texts.json"
CALL "%UTILITIES%\\salvag.bat" "%REPO_ROOT%\\data\\translations\\fr\\texts.json"

ECHO 2. Creazione file HTML e aggiornamento database JSON...
:: Qui viene chiamato lo script add_page.py (o quello che gestisce la logica di creazione)
:: Passando i parametri corretti estratti dal JSON
python "%UTILITIES%\\add_page.py" --id %PAGE_ID% --title "%PAGE_TITLE_IT%" --lat %LAT% --lon %LON% --dist %DISTANCE%

ECHO Operazione completata per {page_data['id']}.
PAUSE
"""

    # 3. Scrittura del file .bat
    output_filename = f"add_{target_page_id}.bat"
    with open(output_filename, 'w', encoding='latin-1') as f: # Latin-1 per compatibilità CMD Windows
        f.write(bat_content)

    print(f"Successo: Creato lo script '{output_filename}' con dati sincronizzati.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        pagina = input("Inserisci l'ID della pagina da generare (es. pugliole): ")
    else:
        pagina = sys.argv[1]
    
    generate_bat_from_config(pagina)