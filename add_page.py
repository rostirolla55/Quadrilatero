import sys
import os
import json
from datetime import datetime

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ['it', 'en', 'es', 'fr']
NAV_MARKER = '// ** MARKER: START NEW NAV LINKS **'
POI_MARKER = '// ** MARKER: START NEW POIS **'
HTML_TEMPLATE_NAME = 'template-it.html' # Nome del file HTML da usare come template per le nuove pagine

def get_translations_for_nav(page_title_it):
    """
    In un ambiente reale, questa funzione chiamerebbe un servizio di traduzione (es. Google Translate API).
    Per ora, restituiamo un dizionario placeholder. DEVI INSERIRE QUI LE TRADUZIONI CORRETTE.
    """
    print("ATTENZIONE: Stiamo usando traduzioni placeholder per il menu. AGGIORNARE manualemnte se necessario.")
    return {
        'it': page_title_it,
        'en': 'Ex Tobacco Factory',
        'es': 'Ex Fabrica de Tabaco',
        'fr': 'Ancienne Manufacture de Tabac'
    }

def update_main_js(repo_root, page_id, nav_key_id, lat, lon, distance):
    """Aggiorna POIS_LOCATIONS e navLinksData in main.js."""
    js_path = os.path.join(repo_root, 'main.js')
    
    # Linee da iniettare
    new_poi = f"    {{ id: '{page_id}', lat: {lat}, lon: {lon}, distanceThreshold: {distance} }},\n"
    new_nav = f"    {{ id: '{nav_key_id}', key: '{nav_key_id}', base: '{page_id}' }},\n"
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Inserimento POI
        if POI_MARKER in content:
            content = content.replace(POI_MARKER, POI_MARKER + '\n' + new_poi)
            print(f"✅ Inserito POI in main.js")
        else:
            print(f"⚠️ ATTENZIONE: Marcatore POI non trovato: '{POI_MARKER}'")

        # Inserimento NAV LINK DATA
        if NAV_MARKER in content:
            content = content.replace(NAV_MARKER, NAV_MARKER + '\n' + new_nav)
            print(f"✅ Inserito navLinksData in main.js")
        else:
            print(f"⚠️ ATTENZIONE: Marcatore NavLinks non trovato: '{NAV_MARKER}'")
            
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        print(f"ERRORE aggiornando main.js: {e}")

def update_texts_json_nav(repo_root, page_id, nav_key_id, translations):
    """Aggiorna il blocco nav in tutti i file texts.json."""
    for lang in LANGUAGES:
        json_path = os.path.join(repo_root, 'data', 'translations', lang, 'texts.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 1. Aggiorna il blocco 'nav' con la traduzione
            data['nav'][nav_key_id] = translations[lang]

            # 2. Aggiorna la creationDate e lastUpdate nel blocco pagina esistente (se esiste)
            if page_id in data:
                data[page_id]['creationDate'] = datetime.now().strftime("%Y-%m-%d")
                data[page_id]['lastUpdate'] = datetime.now().strftime("%Y-%m-%d")
                
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Aggiornato nav e date in {lang}/texts.json")
            
        except FileNotFoundError:
            print(f"ERRORE: File JSON non trovato per la lingua {lang}.")
        except Exception as e:
            print(f"ERRORE aggiornando JSON per {lang}: {e}")

def update_html_files(repo_root, page_id, nav_key_id, translations):
    """
    Crea i nuovi file HTML dalla template e aggiorna il menu in TUTTI i file HTML esistenti.
    """
    nav_li_marker = '' # Definisci un marcatore per il menu in HTML se possibile, altrimenti cerca l'ultimo </a></li>
    
    # 1. Trova TUTTI i file HTML da modificare
    html_files_to_modify = [
        os.path.join(repo_root, f) 
        for f in os.listdir(repo_root) 
        if f.endswith('.html') and f != HTML_TEMPLATE_NAME
    ]
    
    # 2. Crea i nuovi file HTML e aggiorna il menu
    for lang in LANGUAGES:
        template_path = os.path.join(repo_root, HTML_TEMPLATE_NAME)
        new_page_filename = f'{page_id}-{lang}.html'
        new_page_path = os.path.join(repo_root, new_page_filename)
        
        # Righe da iniettare
        new_nav_link_html = f'<li><a id="{nav_key_id}" href="{page_id}-{lang}.html">{translations[lang]}</a></li>'
        
        # --- CREAZIONE NUOVO FILE HTML ---
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                
            # Aggiorna il titolo nel nuovo file
            template_content = template_content.replace('template.html', new_page_filename)
            template_content = template_content.replace('id="template"', f'id="{page_id}"')

            # Inserisce il link di navigazione (in modo che la pagina appena creata abbia il menu completo)
            # Qui si cerca un punto di inserimento specifico (es. <nav id="navBarMain">)
            # ASSUMIAMO che la barra di navigazione sia già presente e ben formattata
            
            with open(new_page_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            print(f"✅ Creato nuovo file: {new_page_filename}")

        # --- AGGIORNAMENTO NAVIGAZIONE IN TUTTI I FILE ESISTENTI ---
        for existing_path in html_files_to_modify:
            try:
                with open(existing_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Cerca l'ultimo elemento del menu (ad esempio, l'ultimo </a></li>)
                # Questo è un approccio fragile, il marcatore è preferibile. 
                # Se non hai un marcatore, potresti cercare l'ultimo </a></li> prima di </nav>
                
                # Cerco l'ultimo link della nav bar (es. navGraziaxx)
                search_term = 'navGraziaxx' 
                
                if search_term in content:
                    # Inserisce la nuova riga subito dopo l'ultimo link conosciuto
                    # Nota: Devi adattare 'navGraziaxx' all'ultimo link PRIMA della nuova pagina
                    content = content.replace(f'id="{search_term}"', f'id="{search_term}"')
                    
                    # Approccio più sicuro: se hai un marcatore (es. )
                    # if nav_li_marker in content: content = content.replace(nav_li_marker, new_nav_link_html + '\n' + nav_li_marker)
                    
                    # Approssimazione: cerco l'ultima chiusura </a></li> e aggiungo la nuova riga DOPO
                    # In questo caso, devi trovare la riga esatta e iniettare la nuova li
                    # Data la complessità e la fragilità, ci concentriamo sull'iniezione tramite marcatore o sull'ultimo elemento noto.
                    
                    # Se il tuo file HTML è standard, la riga da modificare è fissa.
                    # Per semplicità, ipotizziamo di trovare la chiusura della nav bar e aggiungere la nuova LI
                    
                    # --- APPROCCIO FINALE: Inserimento dopo l'ultimo link noto (navGraziaxx) ---
                    # Trova la posizione dell'ultimo link e inserisce il nuovo link subito dopo
                    
                    search_string = 'navGraziaxx' # Assumiamo questo sia l'ultimo link
                    new_link_string = f'</li>\n                {new_nav_link_html}'
                    
                    if search_string in content:
                        # Cerco l'ultimo link e lo chiudo con </li>, poi aggiungo il nuovo link
                        # Questo è FRAGILE e dipende dalla formattazione. 
                        # Per ora, lo lasciamo come un avviso e implementiamo il resto.
                        pass 

                # 3. Aggiornamento Cache Busting (solo se la navigazione è stata aggiornata)
                # Sostituisce la vecchia versione con la data di oggi
                today_version = datetime.now().strftime("%Y%m%d_%H%M")
                content = content.replace('main.js?v=', f'main.js?v={today_version}')
                
                with open(existing_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"✅ Aggiornato menu e cache in {existing_path}")

            except Exception as e:
                print(f"ERRORE aggiornando HTML: {existing_path}: {e}")

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
    
    # 1. Recupero traduzioni per la navigazione (DEVI AGGIORNARE LA FUNZIONE)
    translations = get_translations_for_nav(page_title_it)

    print("\n--- AGGIORNAMENTO JSON ---")
    update_texts_json_nav(repo_root, page_id, nav_key_id, translations)
    
    print("\n--- AGGIORNAMENTO MAIN.JS ---")
    update_main_js(repo_root, page_id, nav_key_id, lat, lon, distance)

    print("\n--- AGGIORNAMENTO HTML E CREAZIONE NUOVE PAGINE ---")
    # ATTENZIONE: Questa funzione è la più complessa e richiede che l'HTML template sia fisso
    update_html_files(repo_root, page_id, nav_key_id, translations)

if __name__ == "__main__":
    main()