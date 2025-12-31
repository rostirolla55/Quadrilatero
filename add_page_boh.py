import sys
import os
import json
import datetime
import shutil
import re

# --- CONFIGURAZIONI ---
LANGUAGES = ['it', 'en', 'es', 'fr']
NAV_MARKER = '// ** MARKER: START NEW NAV LINKS **' 
POI_MARKER = '// ** MARKER: START NEW POIS **' 
HTML_NAV_MARKER = '</ul>' 
TEMPLATE_NAMES = ['template-it.html', 'template.html']

def update_main_js(repo_root, page_id, nav_key_id, lat, lon, distance):
    """Aggiorna la logica di prossimità e il routing nel file main.js"""
    js_path = os.path.join(repo_root, 'main.js')
    if not os.path.exists(js_path): return
    with open(js_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    id_pattern = f"id: '{page_id}'"
    nav_pattern = f"id: '{nav_key_id}'"
    
    # Verifica se esistono già per evitare duplicati
    exists_poi = any(id_pattern in l for l in lines)
    exists_nav = any(nav_pattern in l for l in lines)

    for line in lines:
        if POI_MARKER in line and not exists_poi:
            # Assicura la virgola nel POI precedente se necessario
            if new_lines and not new_lines[-1].strip().endswith(',') and '[' not in new_lines[-1]:
                new_lines[-1] = new_lines[-1].rstrip() + ',\n'
            new_lines.append(f"    {{ id: '{page_id}', lat: {lat}, lon: {lon}, distanceThreshold: {distance} }}\n")
        
        elif NAV_MARKER in line and not exists_nav:
            if new_lines and not new_lines[-1].strip().endswith(',') and '[' not in new_lines[-1]:
                new_lines[-1] = new_lines[-1].rstrip() + ',\n'
            new_lines.append(f"    {{ id: '{nav_key_id}', key: '{nav_key_id}', base: '{page_id}' }}\n")
            
        new_lines.append(line)

    with open(js_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def init_texts_json(repo_root, page_id, nav_key_id, initial_title):
    """Inizializza il nodo nel file texts.json. Verrà poi rifinito dal Blocco 3."""
    for lang in LANGUAGES:
        path = os.path.join(repo_root, 'data', 'translations', lang, 'texts.json')
        if not os.path.exists(path): continue
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Inserimento chiave di navigazione
        if 'nav' not in data: data['nav'] = {}
        data['nav'][nav_key_id] = initial_title 

        # Inizializzazione struttura base a 20 campi (tutti i valori qui sono placeholder)
        # Il manual_key_updater (Blocco 3) sovrascriverà questi campi con i dati reali.
        data[page_id] = {
            "pageTitle": initial_title,
            "mainText": "", 
            "mainText1": f"{lang}_{page_id}_maintext1.html",
            "mainText2": f"{lang}_{page_id}_maintext2.html",
            "mainText3": f"{lang}_{page_id}_maintext3.html",
            "mainText4": "",
            "mainText5": "",
            "playAudioButton": "Play",
            "pauseAudioButton": "Stop",
            "headImage": "placeholder.jpg",
            "imageSource1": f"{page_id}/img1.jpg",
            "imageSource2": f"{page_id}/img2.jpg",
            "imageSource3": "",
            "imageSource4": "",
            "imageSource5": "",
            "sourceText": "",
            "creationDate": datetime.datetime.now().strftime("%Y-%m-%d"),
            "lastUpdate": "",
            "audioSource": ""
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def create_html_and_update_nav(repo_root, page_id, nav_key_id):
    """Crea i file HTML fisici e aggiorna la barra di navigazione in tutti i file."""
    # Trova il template
    template_path = next((os.path.join(repo_root, t) for t in TEMPLATE_NAMES if os.path.exists(os.path.join(repo_root, t))), None)
    if not template_path: return

    # 1. Crea i file specifici per la nuova pagina
    for lang in LANGUAGES:
        target_name = f"{page_id}.html" if lang == 'it' else f"{page_id}-{lang}.html"
        target_path = os.path.join(repo_root, target_name)
        
        if not os.path.exists(target_path):
            shutil.copyfile(template_path, target_path)
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read().replace('id="template"', f'id="{page_id}"')
                content = re.sub(r'<html lang="[a-z]{2}">', f'<html lang="{lang}">', content)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)

    # 2. Aggiorna il menu <ul> in tutti i file HTML del sito
    version = datetime.datetime.now().strftime("%y%m%d%H%M")
    for f in os.listdir(repo_root):
        if f.endswith('.html') and 'template' not in f:
            f_p = os.path.join(repo_root, f)
            with open(f_p, 'r', encoding='utf-8') as file:
                content = file.read()
            
            nav_entry = f'<li><a id="{nav_key_id}" href="{page_id}.html">{{{{ {nav_key_id} }}}}</a></li>'
            
            # Se il link non esiste, lo inserisce prima della chiusura della lista
            if f'id="{nav_key_id}"' not in content and HTML_NAV_MARKER in content:
                content = content.replace(HTML_NAV_MARKER, f"    {nav_entry}\n{HTML_NAV_MARKER}")
            
            # Update cache busting per main.js
            content = re.sub(r'main\.js\?v=[0-9A-Z_]*', f'main.js?v={version}', content)
            
            with open(f_p, 'w', encoding='utf-8') as file:
                file.write(content)

def main():
    # Riceve parametri da batch: pageID, navID, Titolo, Lat, Lon, Dist, RepoPath
    if len(sys.argv) < 8:
        print("Parametri insufficienti")
        return
    
    p_id = sys.argv[1]
    n_key = sys.argv[2]
    title = sys.argv[3]
    lat = sys.argv[4]
    lon = sys.argv[5]
    dist = sys.argv[6]
    root = sys.argv[7].strip('"')

    print(f"--- Esecuzione Blocco 2: Infrastruttura per {p_id} ---")
    update_main_js(root, p_id, n_key, lat, lon, dist)
    init_texts_json(root, p_id, n_key, title)
    create_html_and_update_nav(root, p_id, n_key)
    print(f"Infrastruttura completata. Pronta per il Blocco 3.")

if __name__ == "__main__":
    main()