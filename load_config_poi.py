import json
import os
import re

def update_main_js():
    """
    Legge pois_config.json e rigenera le costanti POIS_LOCATIONS e navLinksData
    all'interno del file main.js utilizzando regex per individuare i blocchi.
    """
    config_file = "pois_config.json"
    js_file = "main.js"

    if not os.path.exists(config_file):
        print(f"Errore: {config_file} non trovato.")
        return

    if not os.path.exists(js_file):
        print(f"Errore: {js_file} non trovato.")
        return

    # 1. Caricamento dati dal JSON
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pois = data.get("pois", [])

    # 2. Generazione stringhe JavaScript
    # Generazione POIS_LOCATIONS
    pois_locations_js = "const POIS_LOCATIONS = [\n"
    for i, p in enumerate(pois):
        comma = "," if i < len(pois) - 1 else ""
        pois_locations_js += f"    {{ id: '{p['id']}', lat: {p['lat']}, lon: {p['lon']}, distanceThreshold: {p['threshold']} }}{comma}\n"
    pois_locations_js += "];"

    # Generazione navLinksData
    # Aggiungiamo sempre la Home che solitamente è fissa
    nav_links_js = "const navLinksData = [\n"
    nav_links_js += "    { id: 'navHome', key: 'navHome', base: 'index' },\n"
    for i, p in enumerate(pois):
        comma = "," if i < len(pois) - 1 else ""
        nav_links_js += f"    {{ id: '{p['nav_id']}', key: '{p['nav_id']}', base: '{p['base_name']}' }}{comma}\n"
    nav_links_js += "];"

    # 3. Lettura del file main.js originale
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 4. Sostituzione tramite Regex
    # Sostituisce il blocco POIS_LOCATIONS
    content = re.sub(
        r'const POIS_LOCATIONS = \[.*?\];', 
        pois_locations_js, 
        content, 
        flags=re.DOTALL
    )

    # Sostituisce il blocco navLinksData
    content = re.sub(
        r'const navLinksData = \[.*?\];', 
        nav_links_js, 
        content, 
        flags=re.DOTALL
    )

    # 5. Salvataggio
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("main.js aggiornato con successo con i dati da pois_config.json.")

if __name__ == "__main__":
    update_main_js()