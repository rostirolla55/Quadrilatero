import sys
import os
import json
import datetime
import shutil
import re

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ['it', 'en', 'es', 'fr']
NAV_MARKER = '// ** MARKER: START NEW NAV LINKS **' # Marcatore per main.js
POI_MARKER = '// ** MARKER: START NEW POIS **' # Marcatore per main.js
HTML_NAV_MARKER = '</ul>' # Marcatore per i file HTML: USIAMO </ul> per INSERIRE IN FONDO
HTML_TEMPLATE_NAME = 'template-it.html' # Nome del file HTML da usare come template

# NUOVO MARCATORE PER IL CAMBIO LINGUA
LANGUAGE_SWITCHER_MARKER = '<!-- LANGUAGE_SWITCHER_PLACEHOLDER -->'
LANGUAGE_NAMES = {'it': 'Italiano', 'en': 'English', 'es': 'Español', 'fr': 'Français'}

def get_translations_for_nav(page_title_it):
    """
    Genera traduzioni per il link di navigazione basandosi sul titolo italiano.
    Invece di placeholder fissi, cerchiamo di mappare termini comuni o mantenere
    il nome proprio se non identificato.
    """
    print(f"DEBUG: Generazione traduzioni dinamiche per: '{page_title_it}'")
    
    # Dizionario di mappatura per termini comuni nei titoli (espandibile)
    mapping = {
        "Template": {"en": "Template", "es": "Plantilla", "fr": "Modèle"},
        "Portico": {"en": "Portico", "es": "Pórtico", "fr": "Portique"},
        "Chiesa": {"en": "Church", "es": "Iglesia", "fr": "Église"},
        "Basilica": {"en": "Basilica", "es": "Basílica", "fr": "Basilique"},
        "Statua": {"en": "Statue", "es": "Estatua", "fr": "Statue"},
        "Canale": {"en": "Channel", "es": "Canal", "fr": "Canal"},
        "Santo": {"en": "Saint", "es": "San", "fr": "Saint"},
        "Santa": {"en": "Saint", "es": "San", "fr": "Saint"},
        "Centrale": {"en": "Power Station", "es": "Central", "fr": "Centrale"}
    }

    translations = {'it': page_title_it}
    
    for lang in ['en', 'es', 'fr']:
        translated_title = page_title_it
        for word_it, trans_dict in mapping.items():
            if word_it.lower() in page_title_it.lower():
                reg = re.compile(re.escape(word_it), re.IGNORECASE)
                translated_title = reg.sub(trans_dict[lang], translated_title)
        
        translations[lang] = translated_title

    print(f"✅ Traduzioni generate: {translations}")
    return translations

def update_main_js(repo_root, page_id, nav_key_id, lat, lon, distance):
    """Aggiorna POIS_LOCATIONS e navLinksData in main.js aggiungendo la virgola finale."""
    js_path = os.path.join(repo_root, 'main.js')
    # AGGIUNTA VIRGOLA FINALE: Assicura che la sintassi dell'array JS rimanga valida
    new_poi = f"    {{ id: '{page_id}', lat: {lat}, lon: {lon}, distanceThreshold: {distance} }},"
    new_nav = f"    {{ id: '{nav_key_id}', key: '{nav_key_id}', base: '{page_id}' }},"
    
    # Le linee saranno inserite prima del marker, mantenendo la formattazione pulita
    new_poi_injection = new_poi + '\n' + POI_MARKER
    new_nav_injection = new_nav + '\n' + NAV_MARKER
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Inserimento POI
        if POI_MARKER in content:
            content = content.replace(POI_MARKER, new_poi_injection)
            print(f"✅ Inserito POI in main.js")
        else:
            print(f"⚠️ ATTENZIONE: Marcatore POI non trovato: '{POI_MARKER}'")

        # Inserimento NAV LINK DATA
        if NAV_MARKER in content:
            content = content.replace(NAV_MARKER, new_nav_injection)
            print(f"✅ Inserito navLinksData in main.js")
        else:
            print(f"⚠️ ATTENZIONE: Marcatore NavLinks non trovato: '{NAV_MARKER}'")
            
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"ERRORE aggiornando main.js: {e}")

def update_texts_json_nav(repo_root, page_id, nav_key_id, translations):
    """Aggiorna i file JSON di traduzione."""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # SCHEMA COMPLETO (tutte le chiavi inizializzate)
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
                new_block['audioSource'] = f"{lang}/{page_id}.mp3"
                
                # Aggiungi un placeholder per il testo iniziale
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

def get_target_lang_code(filename):
    """Determina il codice linguistico corretto dal nome del file HTML."""
    match = re.search(r'-([a-z]{2})\.html$', filename)
    if match:
        return match.group(1)
    
    # La pagina base (es. index.html) è trattata a parte o è l'italiano di default
    if filename.endswith('.html') and filename != HTML_TEMPLATE_NAME:
        return 'it_default' 
    return None

def generate_language_switcher(page_id, current_lang):
    """Genera i tag <li> per il cambio lingua."""
    switcher_html = ['<ul class="language-switcher">']
    
    for lang in LANGUAGES:
        # Crea il nome del file specifico per la lingua (es. pittoricarracci-en.html)
        target_file = f'{page_id}-{lang}.html'
        
        # Determina la classe per il link attivo
        is_active = ' active' if lang == current_lang else ''
        
        # Link structure: <a href="pittoricarracci-en.html" lang="en">English</a>
        switcher_html.append(
            f'        <li class="lang-item{is_active}"><a href="{target_file}" lang="{lang}">{LANGUAGE_NAMES[lang]}</a></li>'
        )
        
    switcher_html.append('    </ul>')
    return '\n'.join(switcher_html)

def update_html_files(repo_root, page_id, nav_key_id, translations, page_title_it):
    """
    Aggiorna tutti i file HTML esistenti aggiungendo il link al menu principale.
    Correzione: rimosse le doppie parentesi graffe che causavano errori visivi.
    """
    
    MARKER_MAIN_NAV = '</ul>' # Inseriamo il nuovo link prima della chiusura della lista
    today_version = datetime.datetime.now().strftime("%Y%m%d_%H%M") 

    # Recuperiamo tutti i file HTML nella root
    all_html_files = [
        os.path.join(repo_root, f) 
        for f in os.listdir(repo_root) 
        if f.endswith('.html') and f != 'template-it.html'
    ]
    
    for existing_path in all_html_files:
        try:
            filename = os.path.basename(existing_path)
            
            with open(existing_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verifichiamo se il link esiste già per evitare duplicati
            if f'id="{nav_key_id}"' in content:
                print(f"⚠️ Link già presente in {filename}, salto iniezione.")
                continue

            # Determiniamo la lingua del file attuale per mettere il link corretto
            # Se il file è pittoricarracci-fr.html, il link sarà pittoricarracci-fr.html
            current_lang = 'it'
            for lang in ['en', 'es', 'fr']:
                if f'-{lang}.html' in filename:
                    current_lang = lang
            
            target_href = f'{page_id}-{current_lang}.html' if current_lang != 'it' else f'{page_id}.html'
            # Usiamo il titolo tradotto per quella lingua come testo iniziale
            label = translations.get(current_lang, page_title_it)

            # COSTRUZIONE DEL LINK PULITO (Senza {{ }})
            nav_link_to_insert = f'                <li><a id="{nav_key_id}" href="{target_href}">{label}</a></li>'
            
            # Iniezione prima dell'ultima chiusura </ul> (solitamente il menu nav)
            if MARKER_MAIN_NAV in content:
                parts = content.rsplit(MARKER_MAIN_NAV, 1)
                content = parts[0] + nav_link_to_insert + '\n            ' + MARKER_MAIN_NAV + parts[1]
                
            # Aggiornamento Cache Busting per il JS
            content = re.sub(r'main\.js\?v=[0-9A-Z_]*', f'main.js?v={today_version}', content)
            
            with open(existing_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Menu aggiornato correttamente in {filename}")

        except Exception as e:
            print(f"ERRORE aggiornando HTML {filename}: {e}")
            
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
    
    print("\n=================================================")
    print(f"AVVIO CREAZIONE PAGINA: {page_id}")
    print("=================================================")

    # 1. Recupero traduzioni per la navigazione
    translations = get_translations_for_nav(page_title_it)

    print("\n--- AGGIORNAMENTO JSON ---")
    update_texts_json_nav(repo_root, page_id, nav_key_id, translations)
    
    print("\n--- AGGIORNAMENTO MAIN.JS ---")
    update_main_js(repo_root, page_id, nav_key_id, lat, lon, distance)

    print("\n--- AGGIORNAMENTO HTML E CREAZIONE NUOVE PAGINE ---")
    # L'aggiornamento HTML ora include la creazione dei file specifici per lingua
    update_html_files(repo_root, page_id, nav_key_id, translations, page_title_it)

if __name__ == "__main__":
    main()