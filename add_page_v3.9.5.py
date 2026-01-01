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
HTML_NAV_MARKER = '</ul>' # Marcatore per i file HTML
HTML_TEMPLATE_NAME = 'template-it.html' # Nome del file HTML da usare come template per le lingue

# NUOVO MARCATORE PER IL CAMBIO LINGUA
LANGUAGE_NAMES = {'it': 'Italiano', 'en': 'English', 'es': 'Español', 'fr': 'Français'}

def get_translations_for_nav(page_title_it):
    """Genera traduzioni dinamiche per i titoli di navigazione."""
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
    return translations

def update_main_js(repo_root, page_id, nav_key_id, lat, lon, distance):
    """Aggiorna main.js aggiungendo POI e NavLinksData con gestione virgole."""
    js_path = os.path.join(repo_root, 'main.js')
    new_poi = f"    {{ id: '{page_id}', lat: {lat}, lon: {lon}, distanceThreshold: {distance} }}"
    new_nav = f"    {{ id: '{nav_key_id}', key: '{nav_key_id}', base: '{page_id}' }}"
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if POI_MARKER in line:
                if not any(f"id: '{page_id}'" in l for l in lines):
                    if len(new_lines) > 0 and '}' in new_lines[-1] and not new_lines[-1].strip().endswith(','):
                        new_lines[-1] = new_lines[-1].rstrip() + ',\n'
                    new_lines.append(new_poi + '\n')
                new_lines.append(line)
            elif NAV_MARKER in line:
                if not any(f"id: '{nav_key_id}'" in l for l in lines):
                    if len(new_lines) > 0 and '}' in new_lines[-1] and not new_lines[-1].strip().endswith(','):
                        new_lines[-1] = new_lines[-1].rstrip() + ',\n'
                    new_lines.append(new_nav + '\n')
                new_lines.append(line)
            else:
                new_lines.append(line)
        with open(js_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    except Exception as e:
        print(f"ERRORE main.js: {e}")

def update_texts_json_nav(repo_root, page_id, nav_key_id, translations):
    """Aggiorna i file JSON di traduzione con lo schema completo."""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    NEW_PAGE_SCHEMA = {
        "pageTitle": "", "mainText": "", "mainText1": "", "mainText2": "", "mainText3": "",
        "mainText4": "", "mainText5": "", "playAudioButton": "Ascolta con le cuffie", 
        "pauseAudioButton": "Pausa", "imageSource1": "", "imageSource2": "", "imageSource3": "",
        "imageSource4": "", "imageSource5": "", "sourceText": "",
        "creationDate": current_date, "lastUpdate": current_date, "audioSource": "" 
    }
    for lang in LANGUAGES:
        json_path = os.path.join(repo_root, 'data', 'translations', lang, 'texts.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['nav'][nav_key_id] = translations[lang]
            if page_id not in data:
                new_block = NEW_PAGE_SCHEMA.copy()
                new_block['pageTitle'] = translations[lang]
                new_block['audioSource'] = f"{lang}/{page_id}.mp3"
                if lang in ['it', 'en']: new_block['mainText'] = "Testo iniziale."
                data[page_id] = new_block
            else:
                for key, val in NEW_PAGE_SCHEMA.items():
                    if key not in data[page_id]: data[page_id][key] = val
                data[page_id]['lastUpdate'] = current_date
                data[page_id]['pageTitle'] = translations[lang]
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e: print(f"ERRORE JSON {lang}: {e}")

def create_redirect_html(repo_root, page_id, page_title_it, version):
    """Crea il file xxx.html (reindirizzamento/base) basato sull'esempio carracci.html."""
    file_path = os.path.join(repo_root, f"{page_id}.html")
    content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title_it}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="loading-message"><p>Caricamento dell'applicazione in corso...</p></div>
    <div id="app-wrapper">
        <header class="main-header">
            <button class="menu-toggle" aria-label="Apri menu"><span class="bar"></span><span class="bar"></span><span class="bar"></span></button>
            <div class="right-header-group">
                <div class="language-selector">
                    <button data-lang="it"><img src="public/flag/it.png" alt="Italiano"></button>
                    <button data-lang="en"><img src="public/flag/en.png" alt="English"></button>
                    <button data-lang="es"><img src="public/flag/es.png" alt="Español"></button>
                    <button data-lang="fr"><img src="public/flag/fr.png" alt="Français"></button>
                </div>
                <button id="nearbyPoiButton" style="display:none;" aria-label="Punti di interesse vicini"></button>
            </div>
        </header>
        <nav class="nav-bar-main" id="navBarMain"><div class="nav-bar-content"><ul></ul></div></nav>
        <div id="nearbyMenuPlaceholder" class="nav-bar-nearby"></div>
        <main class="content-body">
            <div class="header-image-container"><img id="headImage" src="" alt="Immagine testata"><h1 class="header-title" id="headerTitle"></h1></div>
            <div class="main-content-area">
                <audio id="audioPlayer"></audio><button id="playAudio" class="play-style">Ascolta</button>
                <p id="mainText"></p><p id="mainText1"></p><img id="pageImage1" src="" style="display: none;">
                <p id="mainText2"></p><img id="pageImage2" src="" style="display: none;">
                <p id="mainText3"></p><img id="pageImage3" src="" style="display: none;">
                <p id="mainText4"></p><img id="pageImage4" src="" style="display: none;">
                <p id="mainText5"></p><img id="pageImage5" src="" style="display: none;">
            </div>
            <footer class="info-footer"><p id="infoSource"></p><p id="infoCreatedDate"></p><p id="infoUpdatedDate"></p></footer>
        </main>
    </div>
    <script type="module" src="main.js?v={version}"></script>
</body>
</html>"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Creato file base: {page_id}.html")

def update_html_files(repo_root, page_id, nav_key_id, translations, page_title_it):
    """Aggiorna i menu di tutti i file e crea le versioni xxx-lang.html."""
    today_version = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # 1. Crea le pagine specifiche per lingua (xxx-it.html, xxx-en.html...)
    template_path = os.path.join(repo_root, HTML_TEMPLATE_NAME)
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            temp_content = f.read()
        for lang in LANGUAGES:
            new_name = f"{page_id}-{lang}.html"
            new_path = os.path.join(repo_root, new_name)
            if not os.path.exists(new_path):
                c = re.sub(r'<title>.*?</title>', f'<title>{translations[lang]}</title>', temp_content)
                c = re.sub(r'main\.js\?v=[0-9A-Z_]*', f'main.js?v={today_version}', c)
                with open(new_path, 'w', encoding='utf-8') as f: f.write(c)
                print(f"✅ Creato: {new_name}")

    # 2. Crea il file xxx.html di base
    create_redirect_html(repo_root, page_id, page_title_it, today_version)

    # 3. Aggiorna i menu di navigazione in tutti i file HTML
    all_htmls = [f for f in os.listdir(repo_root) if f.endswith('.html') and f != HTML_TEMPLATE_NAME]
    for filename in all_htmls:
        path = os.path.join(repo_root, filename)
        with open(path, 'r', encoding='utf-8') as f: content = f.read()
        
        if f'id="{nav_key_id}"' in content: continue

        # Determina la lingua del file per il link (es. se sono in index-en.html, linko a xxx-en.html)
        file_lang = 'it'
        for l in LANGUAGES:
            if f"-{l}.html" in filename: file_lang = l; break
        
        target_href = f"{page_id}-{file_lang}.html"
        label = translations.get(file_lang, page_title_it)
        nav_link = f'                    <li><a id="{nav_key_id}" href="{target_href}">{label}</a></li>'
        
        if '</ul>' in content:
            # Inserisce nel primo <ul> trovato (quello del menu)
            content = content.replace('<ul>', f'<ul>\n{nav_link}', 1)
            content = re.sub(r'main\.js\?v=[0-9A-Z_]*', f'main.js?v={today_version}', content)
            with open(path, 'w', encoding='utf-8') as f: f.write(content)
            print(f"✅ Menu aggiornato in: {filename}")

def main():
    if len(sys.argv) != 8:
        print("Uso: python add_page.py <id> <nav_id> <titolo_it> <lat> <lon> <dist> <root>")
        sys.exit(1)
    p_id, n_id, t_it, lat, lon, dist, root = sys.argv[1:]
    
    trans = get_translations_for_nav(t_it)
    update_texts_json_nav(root, p_id, n_id, trans)
    update_main_js(root, p_id, n_id, lat, lon, dist)
    update_html_files(root, p_id, n_id, trans, t_it)

if __name__ == "__main__":
    main()