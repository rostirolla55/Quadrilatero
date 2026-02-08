import sys
import os
import json
import datetime
import re

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ["it", "en", "es", "fr"]
HTML_TEMPLATE_NAME = "template-it.html"

def get_translations_for_nav(page_title_it):
    """Genera traduzioni automatiche per i file nav-xx.json."""
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
    """Aggiunge il nuovo POI a pois_config.json per l'uso con load_config_poi.py."""
    config_path = os.path.join(root, "pois_config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not any(p.get('id') == page_id for p in data.get('pois', [])):
            new_poi = {
                "id": page_id,
                "lat": float(lat),
                "lon": float(lon),
                "threshold": int(dist),
                "nav_id": nav_key_id,
                "base_name": page_id
            }
            data.setdefault('pois', []).append(new_poi)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Aggiornato pois_config.json.")

def update_nav_json_files(root, page_id, nav_key_id, translations):
    """Aggiorna nav-it.json, nav-en.json, etc. aggiungendo il blocco nuova pagina."""
    for lang in LANGUAGES:
        nav_file = os.path.join(root, f"nav-{lang}.json")
        if os.path.exists(nav_file):
            with open(nav_file, 'r', encoding='utf-8') as f:
                try:
                    nav_data = json.load(f)
                except:
                    nav_data = []
            
            if not any(item.get('id') == nav_key_id for item in nav_data):
                nav_data.append({
                    "id": nav_key_id,
                    "base": page_id,
                    "text": translations[lang]
                })
                with open(nav_file, 'w', encoding='utf-8') as f:
                    json.dump(nav_data, f, indent=2, ensure_ascii=False)
                print(f"Incrementato nav-{lang}.json con la nuova voce menu.")

def update_texts_json(root, page_id, nav_key_id, page_title_it):
    """Crea il blocco contenuti in data/translations/xx/texts.json."""
    for lang in LANGUAGES:
        json_path = os.path.join(root, "data", "translations", lang, "texts.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if page_id not in data:
                data[page_id] = {
                    "pageTitle": page_title_it,
                    "headerTitle": page_title_it,
                    "mainText": f"Contenuto introduttivo per {page_id}...",
                    "mainText1": "", "mainText2": "", "mainText3": "", "mainText4": "", "mainText5": ""
                }
            
            # Assicura che la chiave nav sia presente per le traduzioni manuali residue
            if "nav" in data and nav_key_id not in data["nav"]:
                data["nav"][nav_key_id] = page_title_it

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Aggiornato texts.json ({lang})")

def create_html_files(root, page_id):
    """Genera i 4 file lingua + il file di redirect automatico."""
    template_path = os.path.join(root, HTML_TEMPLATE_NAME)
    if not os.path.exists(template_path):
        print(f"ERRORE: Template {HTML_TEMPLATE_NAME} non trovato.")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # 1. File per ogni lingua (es. carracci-it.html)
    for lang in LANGUAGES:
        target_path = os.path.join(root, f"{page_id}-{lang}.html")
        content = template_content.replace('lang="it"', f'lang="{lang}"')
        
        # Sostituzione link switcher bandierine
        for l in LANGUAGES:
            content = content.replace(f'href="index-{l}.html"', f'href="{page_id}-{l}.html"')

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Creato file lingua: {page_id}-{lang}.html")

    # 2. File di redirect (es. carracci.html)
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
    <p>Redirecting to your language version...</p>
</body>
</html>"""
    with open(redirect_path, "w", encoding="utf-8") as f:
        f.write(redirect_code)
    print(f"Creato file redirect: {page_id}.html")

def main():
    if len(sys.argv) < 8:
        print("Uso: python add_page.py PAGE_ID NAV_KEY_ID TITLE LAT LON DIST ROOT")
        return

    page_id, nav_key_id, title, lat, lon, dist, root = sys.argv[1:8]
    root = root.strip('"')

    # Passo 1: Aggiorna il config dei POI per la sincronizzazione main.js
    update_pois_config(root, page_id, nav_key_id, lat, lon, dist)
    
    # Passo 2: Aggiorna i file di navigazione JSON (nav-xx.json)
    translations = get_translations_for_nav(title)
    update_nav_json_files(root, page_id, nav_key_id, translations)
    
    # Passo 3: Aggiorna i testi e i blocchi mainText nel database JSON
    update_texts_json(root, page_id, nav_key_id, title)
    
    # Passo 4: Generazione fisica dei file HTML
    create_html_files(root, page_id)

    print(f"\nGenerazione completata per '{page_id}'.")
    print("-" * 40)
    print("PROSSIMI PASSI:")
    print(f"1. Esegui 'python load_config_poi.py' per aggiornare main.js con le coordinate.")
    print(f"2. Esegui 'python update_html_from_json.py' per aggiornare i menu in tutto il sito.")

if __name__ == "__main__":
    main()