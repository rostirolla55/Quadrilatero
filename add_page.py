import sys
import os
import json

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ["it", "en", "es", "fr"]
HTML_TEMPLATE_NAME = "template-it.html"

def get_translations_for_nav(page_title_it):
    """Genera traduzioni base per i file di navigazione."""
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
    """Aggiorna i file nav-xx.json nella cartella menu_json."""
    menu_dir = os.path.join(root, "menu_json")
    if not os.path.exists(menu_dir):
        os.makedirs(menu_dir)

    for lang in LANGUAGES:
        nav_file = os.path.join(menu_dir, f"nav-{lang}.json")
        nav_data = []
        
        if os.path.exists(nav_file):
            with open(nav_file, 'r', encoding='utf-8') as f:
                try:
                    content = json.load(f)
                    # Verifica che il contenuto sia effettivamente una lista
                    if isinstance(content, list):
                        nav_data = content
                    else:
                        print(f"ATTENZIONE: {nav_file} non contiene una lista. Resetting...")
                        nav_data = []
                except Exception as e:
                    print(f"Errore lettura {nav_file}: {e}. Creo nuovo.")
                    nav_data = []
        
        # Controllo duplicati sicuro (item deve essere un dizionario)
        exists = any(isinstance(item, dict) and item.get('id') == nav_key_id for item in nav_data)
        
        if not exists:
            nav_data.append({
                "id": nav_key_id,
                "base": page_id,
                "text": translations[lang]
            })
            with open(nav_file, 'w', encoding='utf-8') as f:
                json.dump(nav_data, f, indent=2, ensure_ascii=False)
            print(f"Aggiornato menu_json/nav-{lang}.json")

def update_texts_json(root, page_id, nav_key_id, page_title_it):
    """Aggiorna i file texts.json nelle sottocartelle di data/translations."""
    for lang in LANGUAGES:
        json_path = os.path.join(root, "data", "translations", lang, "texts.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except:
                    data = {}

            if page_id not in data:
                data[page_id] = {
                    "pageTitle": page_title_it,
                    "headerTitle": page_title_it,
                    "mainText": f"Descrizione per {page_id}...",
                    "mainText1": "", "mainText2": "", "mainText3": "", "mainText4": "", "mainText5": ""
                }
            
            if "nav" in data and isinstance(data["nav"], dict):
                if nav_key_id not in data["nav"]:
                    data["nav"][nav_key_id] = page_title_it

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Aggiornato texts.json ({lang})")

def create_html_files(root, page_id):
    """Genera i 5 file HTML (4 lingue + 1 redirect)."""
    template_path = os.path.join(root, HTML_TEMPLATE_NAME)
    if not os.path.exists(template_path):
        print(f"ERRORE: Template {HTML_TEMPLATE_NAME} non trovato.")
        sys.exit(1)

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    for lang in LANGUAGES:
        target_path = os.path.join(root, f"{page_id}-{lang}.html")
        content = template_content.replace('lang="it"', f'lang="{lang}"')
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Creato {page_id}-{lang}.html")

    redirect_path = os.path.join(root, f"{page_id}.html")
    redirect_code = f"""<!DOCTYPE html>
<html>
<head>
    <script>
        const savedLang = localStorage.getItem('Quartiere Porto_lastLang') || 'it';
        window.location.href = '{page_id}-' + savedLang + '.html';
    </script>
</head>
<body><p>Redirecting...</p></body>
</html>"""
    with open(redirect_path, "w", encoding="utf-8") as f:
        f.write(redirect_code)
    print(f"Creato {page_id}.html (Redirect)")

def main():
    if len(sys.argv) < 8:
        print("Parametri insufficienti.")
        sys.exit(1)

    page_id = sys.argv[1]
    nav_key_id = sys.argv[2]
    title = sys.argv[3]
    root = sys.argv[7].strip('"')

    translations = get_translations_for_nav(title)
    
    try:
        update_nav_json_files(root, page_id, nav_key_id, translations)
        update_texts_json(root, page_id, nav_key_id, title)
        create_html_files(root, page_id)
        print(f"\nOperazione per '{page_id}' conclusa con successo.")
    except Exception as e:
        print(f"\nERRORE CRITICO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()