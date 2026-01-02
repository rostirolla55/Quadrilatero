import sys
import os
import json
import datetime
import shutil
import re

# --- CONFIGURAZIONI ---
LANGUAGES = ["it", "en", "es", "fr"]
NAV_MARKER = "// ** MARKER: START NEW NAV LINKS **"
POI_MARKER = "// ** MARKER: START NEW POIS **"
HTML_NAV_MARKER = "</ul>"
HTML_TEMPLATE_NAME = "template-it.html"

def update_main_js(repo_root, page_id, nav_key_id, lat, lon, distance):
    """Inserisce i dati tecnici in main.js nei punti contrassegnati dai marker."""
    js_path = os.path.join(repo_root, 'main.js')
    new_poi = f"    {{ id: '{page_id}', lat: {lat}, lon: {lon}, distanceThreshold: {distance} }}"
    new_nav = f"    {{ id: '{nav_key_id}', key: '{nav_key_id}', base: '{page_id}' }}"
    
    try:
        if not os.path.exists(js_path): return
        with open(js_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if POI_MARKER in line:
                if not any(f"id: '{page_id}'" in l for l in lines):
                    if new_lines and '}' in new_lines[-1] and not new_lines[-1].strip().endswith(','):
                        new_lines[-1] = new_lines[-1].rstrip() + ',\n'
                    new_lines.append(new_poi + '\n')
                new_lines.append(line)
            elif NAV_MARKER in line:
                if not any(f"id: '{nav_key_id}'" in l for l in lines):
                    if new_lines and '}' in new_lines[-1] and not new_lines[-1].strip().endswith(','):
                        new_lines[-1] = new_lines[-1].rstrip() + ',\n'
                    new_lines.append(new_nav + '\n')
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        with open(js_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    except Exception as e:
        print(f"Errore main.js: {e}")

def update_texts_json(repo_root, page_id, nav_key_id, translations):
    """Aggiorna i file di traduzione texts.json."""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    for lang in LANGUAGES:
        json_path = os.path.join(repo_root, 'data', 'translations', lang, 'texts.json')
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"nav": {}}
            
            data.setdefault('nav', {})[nav_key_id] = translations.get(lang, translations['it'])

            if page_id not in data:
                data[page_id] = {
                    "pageTitle": translations.get(lang, translations['it']),
                    "mainText": "", "mainText1": "", "mainText2": "",
                    "mainText3": "", "mainText4": "", "mainText5": "",
                    "playAudioButton": "Ascolta" if lang == "it" else "Play",
                    "pauseAudioButton": "Pausa" if lang == "it" else "Pause",
                    "imageSource1": "", "imageSource2": "", "imageSource3": "",
                    "imageSource4": "", "imageSource5": "", "sourceText": "",
                    "creationDate": current_date, "lastUpdate": current_date,
                    "audioSource": f"{lang}/{page_id}.mp3"
                }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Errore JSON {lang}: {e}")

def update_html_files(repo_root, page_id, nav_key_id, translations):
    """
    Gestisce la creazione dei nuovi file HTML per lingua e aggiorna
    il menu di navigazione in tutti i file esistenti.
    """
    template_path = os.path.join(repo_root, HTML_TEMPLATE_NAME)
    
    # 1. GENERAZIONE DEI NUOVI FILE HTML (es: pagina-en.html)
    for lang in LANGUAGES:
        suffix = "" if lang == "it" else f"-{lang}"
        new_filename = f"{page_id}{suffix}.html"
        new_path = os.path.join(repo_root, new_filename)
        
        if os.path.exists(template_path):
            shutil.copyfile(template_path, new_path)
            with open(new_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Aggiorna attributo lang e ID del body
            content = re.sub(r'<html lang="[a-z]{2}">', f'<html lang="{lang}">', content)
            content = re.sub(r'<body[^>]*>', f'<body id="{page_id}">', content)
            
            with open(new_path, "w", encoding="utf-8") as f:
                f.write(content)

    # 2. INIEZIONE DEL NUOVO LINK NEI MENU DI TUTTI I FILE HTML
    all_html_files = [f for f in os.listdir(repo_root) if f.endswith(".html") and f != HTML_TEMPLATE_NAME]
    
    for filename in all_html_files:
        file_path = os.path.join(repo_root, filename)
        
        # Determina la lingua del file corrente per puntare al link giusto (es: en -> -en.html)
        current_file_lang = "it"
        for l in ["en", "es", "fr"]:
            if f"-{l}.html" in filename:
                current_file_lang = l
                break
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Evita di inserire il link se è già presente
        if f'id="{nav_key_id}"' not in content:
            link_suffix = "" if current_file_lang == "it" else f"-{current_file_lang}"
            target_href = f"{page_id}{link_suffix}.html"
            label = translations.get(current_file_lang, translations['it'])
            
            new_item = f'                    <li><a id="{nav_key_id}" href="{target_href}">{label}</a></li>'
            
            # Inserisce prima dell'ultima chiusura della lista </ul>
            if HTML_NAV_MARKER in content:
                parts = content.rsplit(HTML_NAV_MARKER, 1)
                content = parts[0] + new_item + "\n            " + HTML_NAV_MARKER + parts[1]

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

def main():
    if len(sys.argv) < 8:
        print("Parametri mancanti!")
        return
    
    # Estrazione parametri da riga di comando
    p_id, n_id, title_it, lat, lon, dist, root = sys.argv[1:8]
    root = root.strip('"')
    
    # Sostituisci con il tuo dizionario di traduzioni caricato
    trans = {"it": title_it, "en": title_it, "es": title_it, "fr": title_it}
    
    # Esecuzione workflow
    update_main_js(root, p_id, n_id, lat, lon, dist)
    update_texts_json(root, p_id, n_id, trans)
    update_html_files(root, p_id, n_id, trans)
    
    print(f"Aggiornamento completato con successo per: {title_it}")

if __name__ == "__main__":
    main()