import re
import json
import os

def extract_config_from_js():
    js_file = "main.js"
    output_file = "pois_config.json"

    if not os.path.exists(js_file):
        print(f"Errore: {js_file} non trovato.")
        return

    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Estrazione POIS_LOCATIONS
    # Il pattern ora include: categoria: '...'
    poi_pattern = r"{\s*id:\s*'([^']*)',\s*lat:\s*([\d\.]+),\s*lon:\s*([\d\.]+),\s*distanceThreshold:\s*(\d+),\s*categoria:\s*'([^']*)'\s*}"
    poi_matches = re.findall(poi_pattern, content)
    
    locations_dict = {}
    for match in poi_matches:
        poi_id, lat, lon, threshold, categoria = match
        locations_dict[poi_id] = {
            "id": poi_id,
            "lat": float(lat),
            "lon": float(lon),
            "threshold": int(threshold),
            "categoria": categoria
        }

    # 2. Estrazione navLinksData
    nav_pattern = r"{\s*id:\s*'([^']*)',\s*key:\s*'[^']*',\s*base:\s*'([^']*)'\s*}"
    nav_matches = re.findall(nav_pattern, content)
    
    nav_dict = {}
    for match in nav_matches:
        nav_id, base_name = match
        if base_name != 'index':
            nav_dict[base_name] = nav_id

    # 3. Unione dei dati
    final_pois = []
    for poi_id, data in locations_dict.items():
        nav_id = nav_dict.get(poi_id, f"nav{poi_id.capitalize()}")
        
        poi_entry = {
            "id": data["id"],
            "lat": data["lat"],
            "lon": data["lon"],
            "threshold": data["threshold"],
            "nav_id": nav_id,
            "base_name": poi_id,
            "categoria": data["categoria"] # Salviamo la categoria nel JSON
        }
        final_pois.append(poi_entry)

    # 4. Scrittura JSON
    output_data = {"pois": final_pois}
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("-" * 74)
    print(f"File {output_file} generato con successo!")
    print(f"Estratti {len(final_pois)} punti di interesse.")
    print("-" * 74)

if __name__ == "__main__":
    extract_config_from_js()