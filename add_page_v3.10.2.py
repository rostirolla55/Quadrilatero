import sys
import os
import json
import shutil
import re

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ["it", "en", "es", "fr"]

def get_translations(title_it):
    """Genera traduzioni automatiche di base per i titoli."""
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

def update_texts_and_nav_json(root, page_id, nav_key_id, title_it):
    """Aggiorna i file texts.json e nav-*.json nelle rispettive cartelle."""
    trans = get_translations(title_it)
    
    for lang in LANGUAGES:
        # 1. Aggiornamento texts.json (Dati contenuti pagina)
        texts_path = os.path.join(root, "data", "translations", lang, "texts.json")
        if os.path.exists(texts_path):
            try:
                with open(texts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if page_id not in data:
                    data[page_id] = {
                        "pageTitle": trans[lang],
                        "headerTitle": trans[lang],
                        "mainText": f"Benvenuti a {trans[lang]}...",
                        "mainText1": "", "mainText2": "", "mainText3": "", "mainText4": "", "mainText5": ""
                    }
                    with open(texts_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    print(f" [+] Texts ({lang}): Aggiornato.")
            except Exception as e:
                print(f" [!] Errore Texts ({lang}): {e}")

        # 2. Aggiornamento nav-*.json (Voci Menu Hamburger in menu_json)
        # Questi file sono LISTE [{}, {}]
        nav_json_path = os.path.join(root, "menu_json", f"nav-{lang}.json")
        if os.path.exists(nav_json_path):
            try:
                with open(nav_json_path, "r", encoding="utf-8") as f:
                    nav_data = json.load(f)
                
                if isinstance(nav_data, list):
                    if not any(item.get('id') == nav_key_id for item in nav_data):
                        nav_data.append({
                            "id": nav_key_id,
                            "base": page_id,
                            "text": trans[lang]
                        })
                        with open(nav_json_path, "w", encoding="utf-8") as f:
                            json.dump(nav_data, f, indent=2, ensure_ascii=False)
                        print(f" [+] Nav Menu ({lang}): Voce aggiunta.")
            except Exception as e:
                print(f" [!] Errore Nav Menu ({lang}): {e}")

def sync_main_js_regex(root):
    """Sincronizza main.js leggendo pois_config.json nella root."""
    main_js_path = os.path.join(root, "main.js")
    config_path = os.path.join(root, "pois_config.json")

    if not os.path.exists(main_js_path) or not os.path.exists(config_path):
        print(f" [!] Errore: File non trovati per Regex.\n JS: {main_js_path}\n Config: {config_path}")
        return

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            pois = config_data.get("pois", [])

        with open(main_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Generazione stringhe per POIS_LOCATIONS (come richiesto da load_config_poi.py)
        pois_loc_js = "const POIS_LOCATIONS = [\n"
        for i, p in enumerate(pois):
            comma = "," if i < len(pois) - 1 else ""
            pois_loc_js += f"    {{ id: '{p['id']}', lat: {p['lat']}, lon: {p['lon']}, distanceThreshold: {p['threshold']} }}{comma}\n"
        pois_loc_js += "];"

        # Generazione stringhe per navLinksData
        nav_data_js = "const navLinksData = [\n"
        nav_data_js += "    { id: 'navHome', key: 'navHome', base: 'index' },\n"
        for i, p in enumerate(pois):
            comma = "," if i < len(pois) - 1 else ""
            nav_data_js += f"    {{ id: '{p['nav_id']}', key: '{p['nav_id']}', base: '{p['base_name']}' }}{comma}\n"
        nav_data_js += "];"

        # Sostituzione Regex (DOTALL permette di catturare più righe)
        content = re.sub(r"const POIS_LOCATIONS = \[.*?\];", pois_loc_js, content, flags=re.DOTALL)
        content = re.sub(r"const navLinksData = \[.*?\];", nav_data_js, content, flags=re.DOTALL)

        with open(main_js_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(" [+] main.js sincronizzato via Regex (POIS_LOCATIONS e navLinksData).")
    except Exception as e:
        print(f" [!] Errore Sincronizzazione: {e}")

def main():
    if len(sys.argv) < 8:
        print("Parametri mancanti!")
        return

    page_id, nav_key_id, title, lat, lon, dist, root = sys.argv[1:8]
    root = root.strip('"')

    # 1. Aggiorna i JSON dei testi e dei menu
    update_texts_and_nav_json(root, page_id, nav_key_id, title)

    # 2. Sincronizza main.js (Sostituzione Integrale)
    sync_main_js_regex(root)

    # 3. Gestione HTML
    target_html = os.path.join(root, f"{page_id}.html")
    if not os.path.exists(target_html):
        template = os.path.join(root, "template-it.html")
        if os.path.exists(template):
            shutil.copy(template, target_html)
            print(f" [+] Creato {page_id}.html")

if __name__ == "__main__":
    main()