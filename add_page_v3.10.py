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

def update_nav_json_files(root, page_id, nav_key_id, translations):
    """Aggiorna i file nav-it.json, nav-en.json, etc. aggiungendo la nuova pagina."""
    for lang in LANGUAGES:
        nav_file = os.path.join(root, f"nav-{lang}.json")
        if os.path.exists(nav_file):
            with open(nav_file, 'r', encoding='utf-8') as f:
                try:
                    nav_data = json.load(f)
                except:
                    nav_data = []
            
            # Verifica se esiste già
            if not any(item.get('id') == nav_key_id for item in nav_data):
                new_entry = {
                    "id": nav_key_id,
                    "base": page_id,
                    "text": translations[lang]
                }
                nav_data.append(new_entry)
                with open(nav_file, 'w', encoding='utf-8') as f:
                    json.dump(nav_data, f, indent=2, ensure_ascii=False)
                print(f"Aggiornato nav-{lang}.json")

def update_texts_json(root, page_id, nav_key_id, page_title_it):
    """Crea il blocco contenuti in texts.json per ogni lingua."""
    for lang in LANGUAGES:
        json_path = os.path.join(root, "data", "translations", lang, "texts.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 1. Aggiunta contenuto pagina (mainText1...5)
            if page_id not in data:
                data[page_id] = {
                    "pageTitle": f"{page_title_it} - {lang.upper()}",
                    "headerTitle": page_title_it if lang == 'it' else f"{page_title_it} ({lang})",
                    "mainText": f"Descrizione iniziale per {page_id}...",
                    "mainText1": f"[Contenuto 1 da it_{page_id}_maintext1.html]",
                    "mainText2": "",
                    "mainText3": "",
                    "mainText4": "",
                    "mainText5": ""
                }

            # 2. Aggiunta voce nav nel dizionario globale se manca
            if "nav" in data:
                data["nav"][nav_key_id] = page_title_it # Verrà poi sovrascritto dai nav-lang.json

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Aggiornato texts.json per lingua: {lang}")

def create_html_files(root, page_id):
    """Genera i 4 file HTML della pagina partendo dal template."""
    template_path = os.path.join(root, HTML_TEMPLATE_NAME)
    if not os.path.exists(template_path):
        print(f"ERRORE: Template {HTML_TEMPLATE_NAME} non trovato.")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    for lang in LANGUAGES:
        target_name = f"{page_id}-{lang}.html"
        target_path = os.path.join(root, target_name)
        
        # Sostituzioni base nel template
        content = template_content.replace('lang="it"', f'lang="{lang}"')
        
        # Aggiornamento link switcher (bandierine)
        for l in LANGUAGES:
            content = content.replace(f'href="index-{l}.html"', f'href="{page_id}-{l}.html"')

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Creato file: {target_name}")

def main():
    if len(sys.argv) < 8:
        print("Uso: python add_page.py PAGE_ID NAV_KEY_ID TITLE LAT LON DIST ROOT")
        return

    page_id, nav_key_id, title, lat, lon, dist, root = sys.argv[1:8]
    root = root.strip('"')

    print(f"\n--- AVVIO GENERAZIONE ASSET PER: {page_id} ---")
    
    translations = get_translations_for_nav(title)
    
    # 1. Aggiorna i file JSON di navigazione (per update_html_from_json.py)
    update_nav_json_files(root, page_id, nav_key_id, translations)
    
    # 2. Aggiorna i file texts.json (Database contenuti)
    update_texts_json(root, page_id, nav_key_id, title)
    
    # 3. Crea i file HTML fisici
    create_html_files(root, page_id)
    
    print(f"\nAsset creati con successo.")
    print(f"NOTA: Ricordati di eseguire 'python load_config_poi.py' per aggiornare main.js")
    print(f"e 'python update_html_from_json.py' per aggiornare i menu in tutti gli HTML.")

if __name__ == "__main__":
    main()