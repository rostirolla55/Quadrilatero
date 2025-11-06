import sys
import os
import json
import datetime
import shutil 
import re 

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ['it', 'en', 'es', 'fr']
NAV_MARKER = '// ** MARKER: START NEW NAV LINKS **' # Marcatore per main.js (OK)
POI_MARKER = '// ** MARKER: START NEW POIS **'      # Marcatore per main.js (OK)
HTML_NAV_MARKER = '<ul>'                            # Marcatore per i file HTML (OK: usiamo <ul>)
HTML_TEMPLATE_NAME = 'template-it.html'             # Nome del file HTML da usare come template

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
    
    # Linee da iniettare: RIMOZIONE dell'a capo iniziale e finale per evitare righe vuote
    # Si affida alla formattazione esistente del codice JS
    new_poi = f"    {{ id: '{page_id}', lat: {lat}, lon: {lon}, distanceThreshold: {distance} }},"
    new_nav = f"    {{ id: '{nav_key_id}', key: '{nav_key_id}', base: '{page_id}' }},"
    
    # Per correggere l'indentazione e l'a capo, useremo una tecnica leggermente diversa:
    # Aggiungeremo l'a capo alla riga del nuovo dato, ma non al marcatore.
    new_poi_injection = new_poi + '\n' + POI_MARKER
    new_nav_injection = new_nav + '\n' + NAV_MARKER
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Inserimento POI
        if POI_MARKER in content:
            # Sostituiamo il marcatore con il nuovo POI + a capo + marcatore
            content = content.replace(POI_MARKER, new_poi_injection)
            print(f"✅ Inserito POI in main.js")
        else:
            print(f"⚠️ ATTENZIONE: Marcatore POI non trovato: '{POI_MARKER}'")

        # Inserimento NAV LINK DATA
        if NAV_MARKER in content:
            # Sostituiamo il marcatore con il nuovo Nav Link + a capo + marcatore
            content = content.replace(NAV_MARKER, new_nav_injection)
            print(f"✅ Inserito navLinksData in main.js")
        else:
            print(f"⚠️ ATTENZIONE: Marcatore NavLinks non trovato: '{NAV_MARKER}'")
            
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"ERRORE aggiornando main.js: {e}")

def update_texts_json_nav(repo_root, page_id, nav_key_id, translations):
    """Aggiorna il blocco nav e inizializza il blocco della pagina con tutte le chiavi (SCHEMA COMPLETO)."""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # SCHEMA COMPLETO basato sul blocco 'pioggia3' (tutte le chiavi inizializzate)
    NEW_PAGE_SCHEMA = {
        "pageTitle": "", 
        "mainText": "",
        "mainText1": "",
        "mainText2": "",
        "mainText3": "",
        "mainText4": "",
        "mainText5": "",
        "playAudioButton": "Ascolta con le cuffie", 
        "pauseAudioButton": "Pausa",               
        "imageSource1": "",
        "imageSource2": "",
        "imageSource3": "",
        "imageSource4": "",
        "imageSource5": "",
        "sourceText": "",
        "creationDate": current_date,
        "lastUpdate": current_date,
        "audioSource": "" 
    }
    
    for lang in LANGUAGES:
        json_path = os.path.join(repo_root, 'data', 'translations', lang, 'texts.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 1. Aggiorna il blocco 'nav'
            data['nav'][nav_key_id] = translations[lang]

            # 2. Inizializza/Aggiorna il blocco della pagina
            if page_id not in data:
                # Creazione del blocco per la nuova pagina (Schema completo)
                new_block = NEW_PAGE_SCHEMA.copy()
                new_block['pageTitle'] = translations[lang]
                new_block['audioSource'] = f"Assets/Audio/{lang}/{page_id}.mp3"
                
                # Aggiungi un placeholder per il testo iniziale (IT/EN)
                if lang == 'it' or lang == 'en':
                    new_block['mainText'] = "Testo iniziale per la traduzione."
                
                data[page_id] = new_block
                print(f"✅ Inizializzato NUOVO blocco '{page_id}' in {lang}/texts.json con schema completo.")
            else:
                # Se la pagina esiste, aggiorna date e assicurati che abbia tutte le chiavi richieste
                for key, default_value in NEW_PAGE_SCHEMA.items():
                    if key not in data[page_id]:
                        data[page_id][key] = default_value
                        
                data[page_id]['lastUpdate'] = current_date
                
                # Correggi il titolo: elimina 'title' se presente e usa 'pageTitle'
                if 'title' in data[page_id]:
                    del data[page_id]['title'] 
                data[page_id]['pageTitle'] = translations[lang]
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Aggiornato nav e schema in {lang}/texts.json")
            
        except FileNotFoundError:
            print(f"ERRORE: File JSON non trovato per la lingua {lang}.")
        except Exception as e:
            print(f"ERRORE aggiornando JSON per {lang}: {e}")

def update_html_files(repo_root, page_id, nav_key_id, translations, page_title_it):
    """
    Crea i nuovi file HTML dalla template, aggiorna il menu e il Cache Busting
    in TUTTI i file HTML esistenti (compreso il template).
    """
    
    MARKER = HTML_NAV_MARKER # Il tag <ul> è il marcatore
    
    all_html_files = [
        os.path.join(repo_root, f) 
        for f in os.listdir(repo_root) 
        if f.endswith('.html')
    ]
    today_version = datetime.datetime.now().strftime("%Y%m%d_%H%M") 

    # 1. CREAZIONE E AGGIORNAMENTO NAVIGAZIONE
    for existing_path in all_html_files:
        try:
            filename = os.path.basename(existing_path)
            
            # --- PARTE A: GESTIONE CREAZIONE NUOVO FILE ---
            if filename == HTML_TEMPLATE_NAME:
                # Se è il template, lo usiamo per la creazione, ma lo aggiorniamo dopo.
                pass 
            else:
                # Estrai la lingua dal file esistente
                lang_code = filename.split('-')[-1].replace(".html", "")
                
                # Nome e percorso del nuovo file da creare (es. manifattura-it.html)
                new_page_filename = f'{page_id}-{lang_code}.html'
                new_page_path = os.path.join(repo_root, new_page_filename)

                if lang_code in LANGUAGES and not os.path.exists(new_page_path):
                    # Crea il nuovo file se non esiste, copiando dal template
                    template_path = os.path.join(repo_root, HTML_TEMPLATE_NAME)
                    if os.path.exists(template_path):
                        shutil.copyfile(template_path, new_page_path)
                        
                        # Aggiorna il tag <body> id e i link interni nel nuovo file
                        with open(new_page_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        content = content.replace('id="template"', f'id="{page_id}-{lang_code}"')
                        
                        with open(new_page_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"✅ Creato nuovo file: {new_page_filename}")
                    else:
                        print(f"ERRORE: Template HTML non trovato: {HTML_TEMPLATE_NAME}")


            # --- PARTE B: AGGIORNAMENTO NAVIGAZIONE E CACHE IN TUTTI I FILE (Inclusi Template e Nuovi File) ---
            
            # Per il template usiamo la lingua italiana per i link interni
            if filename == HTML_TEMPLATE_NAME:
                lang_code = 'it' 
            else:
                lang_code = filename.split('-')[-1].replace(".html", "")
            
            with open(existing_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Link da iniettare: il link alla nuova pagina nella lingua corretta
            nav_link_to_insert = (
                f'        <li><a id="{nav_key_id}" href="{page_id}-{lang_code}.html">'
                f'{translations.get(lang_code, page_title_it)}</a></li>'
            )
            
            # 2.1: Iniezione del link nel menu (Sostituiamo <ul> con <ul> + nuovo link)
            injection_string = MARKER + '\n' + nav_link_to_insert 
            
            # Se la riga del link non è già presente E troviamo il marcatore <ul>
            if MARKER in content and nav_link_to_insert not in content:
                content = content.replace(MARKER, injection_string)
                print(f"✅ Aggiunto link a {filename}")
                
            # 2.2: Aggiornamento Cache Busting
            content = re.sub(r'main\.js\?v=([0-9A-Z_]*)', f'main.js?v={today_version}', content)
            
            with open(existing_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Aggiornato cache in {filename}")

        except Exception as e:
            print(f"ERRORE aggiornando HTML: {filename}: {e}")

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