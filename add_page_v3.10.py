import sys
import os
import json
import datetime
import shutil
import re

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ["it", "en", "es", "fr"]
HTML_TEMPLATE_NAME = "template-it.html"

def get_translations_for_nav(page_title_it):
    """Genera traduzioni automatiche semplificate per il menu."""
    mapping = {
        "Basilica": {"en": "Basilica", "es": "Basílica", "fr": "Basilique"},
        "Chiesa": {"en": "Church", "es": "Iglesia", "fr": "Église"},
        "Santa": {"en": "Saint", "es": "San", "fr": "Saint"},
        "Maria": {"en": "Mary", "es": "María", "fr": "Marie"},
        "Maggiore": {"en": "Major", "es": "Mayor", "fr": "Majeure"},
    }
    translations = {"it": page_title_it}
    words = page_title_it.split()
    for lang in ["en", "es", "fr"]:
        translated_words = [mapping.get(w, {}).get(lang, w) for w in words]
        translations[lang] = " ".join(translated_words)
    return translations

def update_pois_config(root, page_id, nav_key_id, lat, lon, dist):
    """Aggiunge il nuovo POI al file pois_config.json."""
    config_path = os.path.join(root, "pois_config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verifica se il POI esiste già
        if not any(p.get('id') == page_id for p in data['pois']):
            new_poi = {
                "id": page_id,
                "lat": float(lat),
                "lon": float(lon),
                "threshold": int(dist),
                "nav_id": nav_key_id,
                "base_name": page_id
            }
            data['pois'].append(new_poi)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Aggiornato pois_config.json con le nuove coordinate.")

def update_nav_json_files(root, page_id, nav_key_id, translations):
    """Aggiorna i file nav-it.json, nav-en.json, etc."""
    for lang in LANGUAGES:
        nav_file = os.path.join(root, f"nav-{lang}.json")
        if os.path.exists(nav_file):
            with open(nav_file, 'r', encoding='utf-8') as f:
                try: nav_data = json.load(f)
                except: nav_data = []
            
            if not any(item.get('id') == nav_key_id for item in nav_data):
                nav_data.append({"id": nav_key_id, "base": page_id, "text": translations[lang]})
                with open(nav_file, 'w', encoding='utf-8') as f:
                    json.dump(nav_data, f, indent=2, ensure_ascii=False)
                print(f"Aggiornato nav-{lang}.json")

def update_texts_json(root, page_id, nav_key_id, page_title_it):
    """Crea il blocco contenuti in texts.json."""
    for lang in LANGUAGES:
        json_path = os.path.join(root, "data", "translations", lang, "texts.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if page_id not in data:
                data[page_id] = {
                    "pageTitle": f"{page_title_it}",
                    "headerTitle": page_title_it,
                    "mainText": f"Descrizione per {page_id}...",
                    "mainText1": "", "mainText2": "", "mainText3": "", "mainText4": "", "mainText5": ""
                }
            if "nav" in data and nav_key_id not in data["nav"]:
                data["nav"][nav_key_id] = page_title_it

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

def create_html_files(root, page_id):
    """Genera i 4 file lingua + il file di redirect."""
    template_path = os.path.join(root, HTML_TEMPLATE_NAME)
    if not os.path.exists(template_path):
        print("ERRORE: Template non trovato.")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # 1. Crea i 4 file per lingua (es. carracci-it.html)
    for lang in LANGUAGES:
        target_path = os.path.join(root, f"{page_id}-{lang}.html")
        content = template_content.replace('lang="it"', f'lang="{lang}"')
        # Sostituzione link lingue nel template
        for l in LANGUAGES:
            content = content.replace(f'href="index-{l}.html"', f'href="{page_id}-{l}.html"')
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Creato: {page_id}-{lang}.html")

    # 2. Crea il file di redirect (es. carracci.html)
    redirect_path = os.path.join(root, f"{page_id}.html")
    redirect_code = f"""<!DOCTYPE html>
<html>
<head>
    <script>
        const LAST_LANG_KEY = 'Quartiere Porto_lastLang';
        const savedLang = localStorage.getItem(LAST_LANG_KEY) || 'it';
        window.location.href = '{page_id}-' + savedLang + '.html';
    </script>
</head>
<body>
    <p>Redirecting...</p>
</body>
</html>"""
    with open(redirect_path, "w", encoding="utf-8") as f:
        f.write(redirect_code)
    print(f"Creato file di redirect: {page_id}.html")

def main():
    if len(sys.argv) < 8:
        print("Uso: python add_page.py PAGE_ID NAV_KEY_ID TITLE LAT LON DIST ROOT")
        return

    page_id, nav_key_id, title, lat, lon, dist, root = sys.argv[1:8]
    root = root.strip('"')

    # 1. Aggiorna configurazione POI (per load_config_poi.py)
    update_pois_config(root, page_id, nav_key_id, lat, lon, dist)
    
    # 2. Aggiorna i file di navigazione
    translations = get_translations_for_nav(title)
    update_nav_json_files(root, page_id, nav_key_id, translations)
    
    # 3. Aggiorna i database testi
    update_texts_json(root, page_id, nav_key_id, title)
    
    # 4. Crea i 5 file HTML (4 lingue + 1 redirect)
    create_html_files(root, page_id)
    
    print(f"\nOperazione completata per {page_id}.")

if __name__ == "__main__":
    main()