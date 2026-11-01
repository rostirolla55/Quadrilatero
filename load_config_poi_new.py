import json
import os
import re

def update_main_js():
    config_file = "pois_config.json"
    js_file = "main.js"

    if not os.path.exists(config_file) or not os.path.exists(js_file):
        print("Errore: Uno dei file non è presente nella cartella.")
        return

    # 1. Caricamento dati dal JSON
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pois = data.get("pois", [])

    # 2. Generazione stringa POIS_LOCATIONS (include categoria, distanceThreshold e ordine_cammino)
    pois_locations_js = "const POIS_LOCATIONS = [\n"
    for i, p in enumerate(pois):
        comma = "," if i < len(pois) - 1 else ""
        categoria = p.get('categoria', 'edificio')
        # Se ordine_cammino non è presente nel JSON, usa 999 come valore predefinito
        ordine = p.get('ordine_cammino', 999)
        
        pois_locations_js += (  
            f"    {{ id: '{p['id']}', lat: {p['lat']}, lon: {p['lon']}, "
            f"distanceThreshold: {p['threshold']}, categoria: '{categoria}', "
            f"ordine_cammino: {ordine} }}{comma}\n"
        )    
    pois_locations_js += "];"

    # 3. Generazione stringa navLinksData (include poiId e ordine_cammino per il menu dinamico)
    nav_links_js = "const navLinksData = [\n"
    nav_links_js += "    { id: 'navHome', key: 'navHome', base: 'index', poiId: 'home', ordine_cammino: 0 },\n"
    for i, p in enumerate(pois):
        comma = "," if i < len(pois) - 1 else ""
        ordine = p.get('ordine_cammino', 999)
        
        nav_links_js += (
            f"    {{ id: '{p['nav_id']}', key: '{p['nav_id']}', "
            f"base: '{p['base_name']}', poiId: '{p['id']}', "
            f"ordine_cammino: {ordine} }}{comma}\n"
        )
    nav_links_js += "];"                              

    # 4. Lettura e Sostituzione nel file main.js
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Sostituzione del blocco POIS_LOCATIONS
    content = re.sub(r'const POIS_LOCATIONS = \[.*?\];', pois_locations_js, content, flags=re.DOTALL)

    # Sostituzione del blocco navLinksData
    content = re.sub(r'const navLinksData = \[.*?\];', nav_links_js, content, flags=re.DOTALL)

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ main.js aggiornato con successo: POIS_LOCATIONS e navLinksData allineati a pois_config.json con ordine_cammino.")

if __name__ == "__main__":
    update_main_js()