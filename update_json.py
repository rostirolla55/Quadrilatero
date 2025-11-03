import json
import sys
import os
import shutil
import re

# add_page.py
# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ['it', 'en', 'es', 'fr'] # <--- DEVE ESSERE QUI
NAV_INSERT_MARKER = '// ** MARKER: START NEW NAV LINKS **'
POI_MARKER = '// ** MARKER: START NEW POIS **'
HTML_TEMPLATE_NAME = 'template-it.html' 
# ------------------------------
def update_html_files(repo_root, page_id, nav_key_id, translations):
    """
    Crea i nuovi file HTML dalla template, aggiorna il menu e il Cache Busting
    in TUTTI i file HTML esistenti.
    """
    
    NAV_INSERT_MARKER = '// MARCATORE$$XX per NAVBARMAIN'
    
    # 1. Trova TUTTI i file HTML nella root
    all_html_files = [
        os.path.join(repo_root, f) 
        for f in os.listdir(repo_root) 
        if f.endswith('.html')
    ]

    print(f"Trovati {len(all_html_files)} file HTML da elaborare.")

    # 2. Loop per creare le nuove pagine e aggiornare i menu
    for lang in LANGUAGES:
        template_path = os.path.join(repo_root, HTML_TEMPLATE_NAME)
        new_page_filename = f'{page_id}-{lang}.html'
        new_page_path = os.path.join(repo_root, new_page_path)
        
        # Righe da iniettare
        new_nav_link_html = f'                <li><a id="{nav_key_id}" href="{page_id}-{lang}.html">{translations[lang]}</a></li>'
        
        # --- CREAZIONE NUOVO FILE HTML (COPIA E MODIFICA IL TEMPLATE) ---
        if os.path.exists(template_path):
            try:
                # Copia il template per la nuova pagina
                shutil.copyfile(template_path, new_page_path)

                # Aggiorna il contenuto interno al nuovo file (nav bar)
                with open(new_page_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Inietta il nuovo link nel menu del file appena creato
                if NAV_INSERT_MARKER in content:
                    content = content.replace(NAV_INSERT_MARKER, new_nav_link_html + '\n' + NAV_INSERT_MARKER)

                # Aggiorna il tag <body> id e il titolo
                content = content.replace('id="template"', f'id="{page_id}-{lang}"')
                
                with open(new_page_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Creato nuovo file: {new_page_filename}")
            except Exception as e:
                print(f"ERRORE nella creazione/modifica del file {new_page_filename}: {e}")
        else:
            print(f"ERRORE: Template HTML non trovato: {HTML_TEMPLATE_NAME}")


    # 3. AGGIORNAMENTO NAVIGAZIONE E CACHE IN TUTTI I FILE ESISTENTI
    for existing_path in all_html_files:
        try:
            with open(existing_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 3.1: Iniezione del link nel menu
            new_nav_link_html_for_file = f'                <li><a id="{nav_key_id}" href="{page_id}-{os.path.basename(existing_path).split("-")[-1].replace(".html", "")}.html">{translations[lang]}</a></li>'
            
            if NAV_INSERT_MARKER in content:
                 # Inietta il link prima del marcatore
                 content = content.replace(NAV_INSERT_MARKER, new_nav_link_html_for_file + '\n' + NAV_INSERT_MARKER)

            # 3.2: Aggiornamento Cache Busting (su main.js)
            # Sostituisce la versione precedente con la data/ora di oggi
            today_version = datetime.now().strftime("%Y%m%d_%H%M")
            
            # Assicurati di trovare e sostituire SOLO la parte della versione
            # Trova la stringa src="main.js?v=..." e sostituisci il valore dopo v=
            # Questa regex è più sicura, ma se il formato è fisso, usiamo una stringa.
            search_string = 'main.js?v=' 
            if search_string in content:
                # Trova la posizione e taglia la parte dopo
                import re
                content = re.sub(r'main\.js\?v=([0-9A-Z_]*)', f'main.js?v={today_version}', content)
            
            with open(existing_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Aggiornato menu e cache in {os.path.basename(existing_path)}")

        except Exception as e:
            print(f"ERRORE aggiornando HTML: {os.path.basename(existing_path)}: {e}")

# Assicurati di aggiungere l'import di 'shutil' e 're' all'inizio del file
import shutil 
import re
if __name__ == "__main__":
    update_json_file()