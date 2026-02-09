import sys
import os
import json
import re

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ["it", "en", "es", "fr"]

def get_translations(title_it):
    """Mappa minima per traduzioni automatiche dei titoli."""
    mapping = {
        "Basilica": {"en": "Basilica", "es": "Basílica", "fr": "Basilique"},
        "Chiesa": {"en": "Church", "es": "Iglesia", "fr": "Église"},
        "Santa": {"en": "Saint", "es": "San", "fr": "Saint"},
    }
    translations = {"it": title_it}
    for lang in ["en", "es", "fr"]:
        trans = title_it
        for k, v in mapping.items():
            trans = trans.replace(k, v[lang])
        translations[lang] = trans
    return translations

def update_json_files(root, page_id, nav_key_id, title_it):
    """Aggiorna texts.json e nav-*.json."""
    trans = get_translations(title_it)
    for lang in LANGUAGES:
        # 1. Update texts.json (Contenuti)
        t_path = os.path.join(root, "data", "translations", lang, "texts.json")
        if os.path.exists(t_path):
            with open(t_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if page_id not in data:
                data[page_id] = {
                    "title": trans[lang],
                    "mainText": f"Descrizione per {trans[lang]}...",
                    "mainText1": "", "mainText2": "", "mainText3": "", "mainText4": "", "mainText5": ""
                }
                with open(t_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

        # 2. Update nav-*.json (Voci Menu)
        n_path = os.path.join(root, "data", "translations", lang, f"nav-{lang}.json")
        if os.path.exists(n_path):
            with open(n_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data[nav_key_id] = trans[lang]
            with open(n_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

def update_main_js_with_regex(root, pois_config_path):
    """
    Legge pois_config.json e sovrascrive integralmente i blocchi 
    navLinks e locations in main.js usando REGEX.
    """
    main_js_path = os.path.join(root, "main.js")
    
    if not os.path.exists(pois_config_path) or not os.path.exists(main_js_path):
        print("Errore: File necessari per Regex non trovati.")
        return

    with open(pois_config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        pois = config.get("pois", [])

    with open(main_js_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Generazione stringhe per main.js
    nav_links_str = "const navLinks = [\n"
    for p in pois:
        nav_links_str += f'    {{ id: "{p["nav_id"]}", target: "{p["id"]}" }},\n'
    nav_links_str += "];"

    locations_str = "const locations = [\n"
    for p in pois:
        locations_str += f'    {{ id: "{p["id"]}", lat: {p["lat"]}, lon: {p["lon"]}, threshold: {p["threshold"]}, nav_id: "{p["nav_id"]}", base_name: "{p["base_name"]}" }},\n'
    locations_str += "];"

    # Sostituzione con Regex (Individua tutto tra 'const navLinks = [' e '];')
    content = re.sub(r"const navLinks\s*=\s*\[[\s\S]*?\];", nav_links_str, content)
    content = re.sub(r"const locations\s*=\s*\[[\s\S]*?\];", locations_str, content)

    with open(main_js_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("main.js sincronizzato con pois_config.json via Regex.")

def main():
    if len(sys.argv) < 8:
        print("Uso: python add_page.py <id> <nav_id> <titolo> <lat> <lon> <dist> <root>")
        return

    page_id, nav_key_id, title, lat, lon, dist, root = sys.argv[1:8]
    root = root.strip('\"')
    pois_config_path = os.path.join(root, "Utilities", "pois_config.json")

    # 1. Aggiorna i file di traduzione
    update_json_files(root, page_id, nav_key_id, title)
    
    # 2. (Opzionale) Se vuoi che lo script aggiorni prima il pois_config.json
    # Qui andrebbe la logica per aggiungere il nuovo POI al file JSON se non esiste.
    
    # 3. Sincronizza main.js
    update_main_js_with_regex(root, pois_config_path)

if __name__ == "__main__":
    main()