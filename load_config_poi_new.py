import json
import os
import re

def update_main_js():
    config_file = "pois_config.json"
    js_file = "main.js"

    if not os.path.exists(config_file) or not os.path.exists(js_file):
        print("Errore: pois_config.json o main.js non trovati.")
        return

    # 1. Carichiamo i dati dal JSON
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pois = data.get("pois", [])

    # 2. Prepariamo il blocco POIS_LOCATIONS
    loc_js = "const POIS_LOCATIONS = [\n"
    for i, p in enumerate(pois):
        sep = "," if i < len(pois) - 1 else ""
        loc_js += f"    {{ id: '{p['id']}', lat: {p['lat']}, lon: {p['lon']}, distanceThreshold: {p['threshold']}, categoria: '{p['categoria']}' }}{sep}\n"
    loc_js += "];"

    # 3. Prepariamo il blocco navLinksData (LA PARTE MANCANTE)
    nav_js = "const navLinksData = {\n"
    for i, p in enumerate(pois):
        sep = "," if i < len(pois) - 1 else ""
        nav_js += f"    '{p['nav_id']}': '{p['id']}'{sep}\n"
    nav_js += "};"

    # 4. Leggiamo il file main.js
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 5. Sostituzione con Regex (molto precise)
    content = re.sub(r"const POIS_LOCATIONS = \[.*?\];", loc_js, content, flags=re.DOTALL)
    content = re.sub(r"const navLinksData = \{.*?\};", nav_js, content, flags=re.DOTALL)

    # 6. Salvataggio
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Sincronizzazione completata! Inseriti {len(pois)} punti di interesse.")

if __name__ == "__main__":
    update_main_js()