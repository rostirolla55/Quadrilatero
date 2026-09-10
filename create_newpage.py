import json
import os

def generate_bat_from_config(target_page_id):
    config_file = "pois_config.json"
    
    if not os.path.exists(config_file):
        print(f"Errore: {config_file} non trovato.")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    page_data = next((p for p in data.get("pois", []) if p["id"] == target_page_id), None)
    
    if not page_data:
        print(f"Errore: Pagina '{target_page_id}' non trovata nel JSON.")
        return

    bat_content = f"""@echo off
ECHO =========================================================
ECHO AGGIUNTA NUOVA PAGINA: {page_data['id']}
ECHO =========================================================

SET "REPO_ROOT=%~dp0"
IF "%REPO_ROOT:~-1%"=="\\" SET "REPO_ROOT=%REPO_ROOT:~0,-1%"
SET "UTILITIES=%REPO_ROOT%\\Utilities"

SET "PAGE_ID={page_data['id']}"
SET "NAV_KEY_ID={page_data['nav_id']}"
SET "PAGE_TITLE_IT=Titolo per {page_data['id']}"
SET "LAT={page_data['lat']}"
SET "LON={page_data['lon']}"
SET "DISTANCE={page_data['threshold']}"

ECHO 1. Backup file...
CALL "%UTILITIES%\\salvag.bat" "%REPO_ROOT%\\main.js"
CALL "%UTILITIES%\\salvag.bat" "%REPO_ROOT%\\data\\translations\\it\\texts.json"

ECHO 2. Esecuzione add_page.py...
python "%REPO_ROOT%\\add_page.py" %PAGE_ID% %NAV_KEY_ID% "%PAGE_TITLE_IT%" %LAT% %LON% %DISTANCE% "%REPO_ROOT%"
IF ERRORLEVEL 1 (
    ECHO.
    ECHO [ERRORE] Lo script add_page.py e' fallito. Interruzione procedura.
    PAUSE
    EXIT /B 1
)

ECHO 3. Aggiornamento main.js e HTML...
python "%REPO_ROOT%\\load_config_poi.py"
python "%REPO_ROOT%\\update_html_from_json.py"

ECHO Procedura completata con successo.
PAUSE
"""

    output_filename = f"add_{target_page_id}.bat"
    with open(output_filename, 'w', encoding='latin-1') as f:
        f.write(bat_content)
    print(f"Creato '{output_filename}' con gestione errori.")

if __name__ == "__main__":
    import sys
    pagina = sys.argv[1] if len(sys.argv) > 1 else input("ID pagina: ")
    generate_bat_from_config(pagina)