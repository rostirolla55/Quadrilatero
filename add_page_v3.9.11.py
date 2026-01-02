import sys
import os
import json
import datetime
import shutil
import re

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ["it", "en", "es", "fr"]
NAV_MARKER = "// ** MARKER: START NEW NAV LINKS **"
POI_MARKER = "// ** MARKER: START NEW POIS **"
HTML_NAV_MARKER = "</ul>"
HTML_TEMPLATE_NAME = "template-it.html"
LANGUAGE_SWITCHER_MARKER = "<!-- LANGUAGE_SWITCHER_PLACEHOLDER -->"

LANGUAGE_NAMES = {"it": "Italiano", "en": "English", "es": "Español", "fr": "Français"}

def get_translations_for_nav(page_title_it):
    """Genera traduzioni automatiche per il menu basate su parole chiave."""
    mapping = {
        "Basilica": {"en": "Basilica", "es": "Basílica", "fr": "Basilique"},
        "Chiesa": {"en": "Church", "es": "Iglesia", "fr": "Église"},
        "Santa": {"en": "Saint", "es": "San", "fr": "Saint"},
        "Maria": {"en": "Mary", "es": "María", "fr": "Marie"},
        "Maggiore": {"en": "Major", "es": "Mayor", "fr": "Majeure"},
        "Portico": {"en": "Portico", "es": "Pórtico", "fr": "Portique"},
        "Statua": {"en": "Statue", "es": "Estatua", "fr": "Statue"},
        "Canale": {"en": "Channel", "es": "Canal", "fr": "Canal"}
    }
    translations = {"it": page_title_it}
    for lang in ["en", "es", "fr"]:
        translated_title = page_title_it
        for word_it, trans_dict in mapping.items():
            if word_it.lower() in page_title_it.lower():
                reg = re.compile(re.escape(word_it), re.IGNORECASE)
                translated_title = reg.sub(trans_dict[lang], translated_title)
        translations[lang] = translated_title
    return translations

def update_main_js(repo_root, page_id, nav_key_id, lat, lon, distance):
    """Aggiorna main.js gestendo virgole e prevenendo duplicati."""
    js_path = os.path.join(repo_root, 'main.js')
    if not os.path.exists(js_path):
        return

    new_poi_line = f"    {{ id: '{page_id}', lat: {lat}, lon: {lon}, distanceThreshold: {distance} }},"
    new_nav_line = f"    {{ id: '{nav_key_id}', key: '{nav_key_id}', base: '{page_id}' }},"

    with open(js_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    
    # Controllo duplicati basato sulla tua logica
    poi_exists = any(f"id: '{page_id}'" in l for l in lines)
    nav_exists = any(f"id: '{nav_key_id}'" in l for l in lines)

    for i, line in enumerate(lines):
        if POI_MARKER in line:
            if not poi_exists:
                # Logica riga per riga per la virgola precedente
                if len(new_lines) > 0:
                    prev = new_lines[-1].rstrip()
                    if prev.endswith('}') and not prev.endswith('},'):
                        new_lines[-1] = prev + ",\n"
                new_lines.append(new_poi_line + "\n")
            new_lines.append(line)
        elif NAV_MARKER in line:
            if not nav_exists:
                # Logica riga per riga per la virgola precedente
                if len(new_lines) > 0:
                    prev = new_lines[-1].rstrip()
                    if prev.endswith('}') and not prev.endswith('},'):
                        new_lines[-1] = prev + ",\n"
                new_lines.append(new_nav_line + "\n")
            new_lines.append(line)
        else:
            new_lines.append(line)

    with open(js_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("✅ main.js aggiornato (con controllo duplicati e virgole).")

def update_texts_json_nav(repo_root, page_id, nav_key_id, translations):
    """Aggiorna i file JSON creando cartelle se mancanti (tua logica)."""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    NEW_PAGE_SCHEMA = {
        "pageTitle": "", "mainText": "", "mainText1": "", "mainText2": "",
        "mainText3": "", "mainText4": "", "mainText5": "",
        "playAudioButton": "Ascolta con le cuffie", "pauseAudioButton": "Pausa",
        "imageSource1": "", "imageSource2": "", "imageSource3": "",
        "imageSource4": "", "imageSource5": "", "sourceText": "",
        "creationDate": current_date, "lastUpdate": current_date, "audioSource": "" 
    }
    
    for lang in LANGUAGES:
        json_path = os.path.join(repo_root, 'data', 'translations', lang, 'texts.json')
        
        # Crea cartella se manca (tua logica di protezione)
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"nav": {}}

            if 'nav' not in data: data['nav'] = {}
            data['nav'][nav_key_id] = translations[lang]

            if page_id not in data:
                new_block = NEW_PAGE_SCHEMA.copy()
                new_block['pageTitle'] = translations[lang]
                new_block['audioSource'] = f"{lang}/{page_id}.mp3"
                data[page_id] = new_block
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"✅ JSON {lang} aggiornato.")
        except Exception as e:
            print(f"ERRORE JSON {lang}: {e}")

def update_html_files(repo_root, page_id, nav_key_id, translations, page_title_it):
    """Crea file con suffissi e aggiorna i menu contestualmente."""
    template_path = os.path.join(repo_root, HTML_TEMPLATE_NAME)
    today_version = datetime.datetime.now().strftime("%Y%m%d_%H%M")

    # 1. Creazione file per ogni lingua con suffisso
    for lang in LANGUAGES:
        new_filename = f"{page_id}-{lang}.html"
        new_path = os.path.join(repo_root, new_filename)

        if not os.path.exists(new_path):
            shutil.copyfile(template_path, new_path)
            with open(new_path, "r", encoding="utf-8") as f:
                content = f.read()

            content = content.replace('id="template"', f'id="{page_id}"')
            content = re.sub(r'<html lang="[a-z]{2}">', f'<html lang="{lang}">', content)

            # Switcher coerente
            switcher_html = ['<ul class="language-switcher">']
            for l in LANGUAGES:
                is_active = " active" if l == lang else ""
                switcher_html.append(f'        <li class="lang-item{is_active}"><a href="{page_id}-{l}.html" lang="{l}">{LANGUAGE_NAMES[l]}</a></li>')
            switcher_html.append("    </ul>")
            
            if LANGUAGE_SWITCHER_MARKER in content:
                content = content.replace(LANGUAGE_SWITCHER_MARKER, "\n".join(switcher_html))

            with open(new_path, "w", encoding="utf-8") as f:
                f.write(content)

    # 2. Aggiornamento menu in tutti i file .html esistenti
    all_files = [f for f in os.listdir(repo_root) if f.endswith(".html") and f != HTML_TEMPLATE_NAME]
    for filename in all_files:
        file_path = os.path.join(repo_root, filename)
        
        file_lang = "it"
        for l in LANGUAGES:
            if f"-{l}.html" in filename:
                file_lang = l

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if f'id="{nav_key_id}"' not in content:
            target_href = f"{page_id}-{file_lang}.html"
            label = translations.get(file_lang, page_title_it)
            nav_link = f'                <li><a id="{nav_key_id}" href="{target_href}">{label}</a></li>'

            if HTML_NAV_MARKER in content:
                parts = content.rsplit(HTML_NAV_MARKER, 1)
                content = parts[0] + nav_link + "\n            " + HTML_NAV_MARKER + parts[1]

            content = re.sub(r"main\.js\?v=[0-9A-Z_]*", f"main.js?v={today_version}", content)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

def main():
    if len(sys.argv) < 8: return
    page_id, nav_key_id, title, lat, lon, dist, root = sys.argv[1:8]
    root = root.strip('"')

    print(f"Aggiornamento V3.9.3 (Full Logic) in corso per {page_id}...")
    translations = get_translations_for_nav(title)

    update_main_js(root, page_id, nav_key_id, lat, lon, dist)
    update_texts_json_nav(root, page_id, nav_key_id, translations)
    update_html_files(root, page_id, nav_key_id, translations, title)
    print("Completato.")

if __name__ == "__main__":
    main()