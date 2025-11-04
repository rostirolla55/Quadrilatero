import sys
import os
import json
import datetime # Importazione corretta della libreria completa
import shutil 
import re 

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ['it', 'en', 'es', 'fr']
NAV_MARKER = '// ** MARKER: START NEW NAV LINKS **' # Marcatore per main.js
POI_MARKER = '// ** MARKER: START NEW POIS **'       # Marcatore per main.js
HTML_NAV_MARKER = '// ** MARKER: START NEW HTML LINKS **' # Marcatore per i file HTML
HTML_TEMPLATE_NAME = 'template-it.html' # Nome del file HTML da usare come template per le nuove pagine

# ----------------------------------------------------------------------------------

def get_translations_for_nav(page_title_it):
    """
    Ritorna le traduzioni hardcoded per il link di navigazione.
    """
    print("ATTENZIONE: Stiamo usando traduzioni placeholder per il menu. AGGIORNARE manualemnte se necessario.")
    return {
        'it': page_title_it,
        'en': 'Ex Tobacco Factory',
        'es': 'Ex Fabrica de Tabaco',
        'fr': 'Ancienne Manufacture de Tabac'
    }

# File: add_page.py

def update_main_js(repo_root, page_id, nav_key_id, lat, lon, distance):
    """Aggiorna POIS_LOCATIONS e navLinksData in main.js."""
    js_path = os.path.join(repo_root, 'main.js')
    
    # Linee da iniettare
    # NOTA: Le linee da iniettare devono includere il marcatore per il prossimo inserimento

    new_poi = f"    {{ id: '{page_id}', lat: {lat}, lon: {lon}, distanceThreshold: {distance} }},\n"
    new_nav = f"    {{ id: '{nav_key_id}', key: '{nav_key_id}', base: '{page_id}' }},\n"
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Inserimento POI (Corretto: inietta il nuovo POI dopo il marcatore)
        if POI_MARKER in content:
            # Inseriamo la nuova riga e rigeneriamo il marcatore subito sotto per il prossimo utilizzo
            content = content.replace(POI_MARKER, POI_MARKER + '\n' + new_poi)
            print(f"✅ Inserito POI in main.js")
        else:
            print(f"⚠️ ATTENZIONE: Marcatore POI non trovato: '{POI_MARKER}'")

        # Inserimento NAV LINK DATA (Corretto: inietta il nuovo link dopo il marcatore)
        if NAV_MARKER in content:
            # Inseriamo la nuova riga e rigeneriamo il marcatore subito sotto per il prossimo utilizzo
            content = content.replace(NAV_MARKER, NAV_MARKER + '\n' + new_nav)
            print(f"✅ Inserito navLinksData in main.js")
        else:
            print(f"⚠️ ATTENZIONE: Marcatore NavLinks non trovato: '{NAV_MARKER}'")
            
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"ERRORE aggiornando main.js: {e}")
def update_texts_json_nav(repo_root, page_id, nav_key_id, translations):
    """Aggiorna il blocco nav e inizializza il blocco della pagina in tutti i file texts.json."""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    for lang in LANGUAGES:
        json_path = os.path.join(repo_root, 'data', 'translations', lang, 'texts.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 1. Aggiorna il blocco 'nav' con la traduzione
            data['nav'][nav_key_id] = translations[lang]

            # 2. Inizializza il blocco della pagina se non esiste, altrimenti aggiorna le date
            if page_id not in data:
                # Creazione del blocco per la nuova pagina (es. 'manifattura')
                data[page_id] = {
                    "title": translations[lang],
                    "creationDate": current_date,
                    "lastUpdate": current_date,
                    # INIZIALIZZAZIONE NUOVO CAMPO (basato sul tuo feedback)
                    "audioSource": f"Assets/Audio/{lang}/{page_id}.mp3"
                }
                print(f"✅ Inizializzato nuovo blocco '{page_id}' in {lang}/texts.json")
            else:
                # Se la pagina esiste già (per future esecuzioni), aggiorna solo le date
                data[page_id]['lastUpdate'] = current_date
            
            with open(json_path, 'w', encoding='utf-8') as f:
                # Usa indent=4 per formattare bene il JSON
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Aggiornato nav in {lang}/texts.json")
            
        except FileNotFoundError:
            print(f"ERRORE: File JSON non trovato per la lingua {lang}.")
        except Exception as e:
            print(f"ERRORE aggiornando JSON per {lang}: {e}")
def update_html_files(repo_root, page_id, nav_key_id, translations, page_title_it):
    """
    Crea i nuovi file HTML dalla template, aggiorna il menu e il Cache Busting
    in TUTTI i file HTML esistenti.
    """
    
    # 1. Trova TUTTI i file HTML nella root
    all_html_files = [
        os.path.join(repo_root, f) 
        for f in os.listdir(repo_root) 
        if f.endswith('.html')
    ]

    print(f"Trovati {len(all_html_files)} file HTML da elaborare.")

    # Calcola la versione una sola volta
    today_version = datetime.datetime.now().strftime("%Y%m%d_%H%M") 

    # Loop su tutte le lingue per creare le nuove pagine
    for lang in LANGUAGES:
        template_path = os.path.join(repo_root, HTML_TEMPLATE_NAME)
        new_page_filename = f'{page_id}-{lang}.html'
        new_page_path = os.path.join(repo_root, new_page_filename)
        
        # Righe da iniettare: il link della nuova pagina. Usa la traduzione per la lingua corrente.
        new_nav_link_html = (
            f'                <li><a id="{nav_key_id}" href="{page_id}-{lang}.html">'
            f'{translations.get(lang, page_id)}</a></li>' # Usiamo .get() per sicurezza
        )
        
        # --- CREAZIONE NUOVO FILE HTML (COPIA E MODIFICA IL TEMPLATE) ---
        if os.path.exists(template_path):
            try:
                # Leggi il template
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Aggiorna il tag <body> id
                content = content.replace('id="template"', f'id="{page_id}-{lang}"')

                # Inietta il NUOVO link nel menu del file appena creato
                if HTML_NAV_MARKER in content:
                    # NOTA: Qui rimpiazziamo HTML_NAV_MARKER, non NAV_MARKER di main.js
                    content = content.replace(HTML_NAV_MARKER, new_nav_link_html + '\n' + HTML_NAV_MARKER)
                
                # Applica il Cache Busting
                content = re.sub(r'main\.js\?v=([0-9A-Z_]*)', f'main.js?v={today_version}', content)

                with open(new_page_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Creato nuovo file: {new_page_filename}")
                
            except Exception as e:
                print(f"ERRORE nella creazione/modifica del file {new_page_filename}: {e}")
        else:
            print(f"ERRORE: Template HTML non trovato: {HTML_TEMPLATE_NAME}")


    # 2. AGGIORNAMENTO NAVIGAZIONE E CACHE IN TUTTI I FILE ESISTENTI
    for existing_path in all_html_files:
        try:
            # Salta il file template
            if os.path.basename(existing_path) == HTML_TEMPLATE_NAME:
                 continue
            
            # Estrai la lingua del file esistente (es. da index-it.html ottiene it)
            lang_code = os.path.basename(existing_path).split('-')[-1].replace(".html", "")
            
            with open(existing_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Righe da iniettare: il link alla pagina "manifattura" nella lingua corretta
            nav_link_to_insert = (
                f'                <li><a id="{nav_key_id}" href="{page_id}-{lang_code}.html">'
                f'{translations.get(lang_code, page_title_it)}</a></li>'
            )
            
            # 2.1: Iniezione del link nel menu (Solo se il link non è già presente E il marcatore è presente)
            if HTML_NAV_MARKER in content and nav_link_to_insert not in content:
                 content = content.replace(HTML_NAV_MARKER, nav_link_to_insert + '\n' + HTML_NAV_MARKER)
                 print(f"✅ Aggiunto link a {os.path.basename(existing_path)}")

            # 2.2: Aggiornamento Cache Busting (su main.js)
            content = re.sub(r'main\.js\?v=([0-9A-Z_]*)', f'main.js?v={today_version}', content)
            
            with open(existing_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Aggiornato cache in {os.path.basename(existing_path)}")

        except Exception as e:
            print(f"ERRORE aggiornando HTML: {os.path.basename(existing_path)}: {e}")

# ----------------------------------------------------------------------------------

def main():
    if len(sys.argv) != 8:
        print("Uso: python add_page.py <page_id> <nav_key_id> <page_title_it> <lat> <lon> <distance> <repo_root>")
        sys.exit(1)

    page_id = sys.argv[1]
    nav_key_id = sys.argv[2]
    page_title_it = sys.argv[3]
    lat = sys.argv[4]
    lon = sys.argv[5]
    distance = sys.argv[6]
    repo_root = sys.argv[7]
    
    # 1. Recupero traduzioni per la navigazione
    translations = get_translations_for_nav(page_title_it)

    print("\n--- AGGIORNAMENTO JSON ---")
    update_texts_json_nav(repo_root, page_id, nav_key_id, translations)
    
    print("\n--- AGGIORNAMENTO MAIN.JS ---")
    update_main_js(repo_root, page_id, nav_key_id, lat, lon, distance)

    print("\n--- AGGIORNAMENTO HTML E CREAZIONE NUOVE PAGINE ---")
    # Passa page_title_it come richiesto dalla funzione update_html_files
    update_html_files(repo_root, page_id, nav_key_id, translations, page_title_it)

if __name__ == "__main__":
    main()