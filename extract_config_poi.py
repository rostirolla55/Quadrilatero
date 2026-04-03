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
    # Questa Regex cerca i 5 campi base e rende OPZIONALI i 2 campi visual_lat/lon
    poi_pattern = r"\{\s*id:\s*'([^']*)',\s*lat:\s*([\d\.]+),\s*lon:\s*([\d\.]+),\s*distanceThreshold:\s*(\d+),\s*categoria:\s*'([^']*)'(?:,\s*visual_lat:\s*([\d\.]+))?(?:,\s*visual_lon:\s*([\d\.]+))?\s*\}"
    poi_matches = re.findall(poi_pattern, content)
    
    locations_dict = {}

    for match in poi_matches:
        # match avrà sempre 7 elementi grazie ai gruppi opzionali (?:...)?, 
        # ma gli ultimi due saranno stringhe vuote se non presenti nel JS
        poi_id, lat, lon, threshold, categoria, v_lat, v_lon = match
        
        locations_dict[poi_id] = {
            "id": poi_id,
            "lat": float(lat),
            "lon": float(lon),
            "threshold": int(threshold),
            "categoria": categoria,
            # Se v_lat/v_lon sono vuoti, usa lat/lon originali
            "visual_lat": float(v_lat) if v_lat else float(lat),
            "visual_lon": float(v_lon) if v_lon else float(lon)
        }

    # 2. Estrazione navLinksData (rimane invariata)
    nav_pattern = r"\{\s*id:\s*'([^']*)',\s*key:\s*'[^']*',\s*base:\s*'([^']*)'\s*\}"
    nav_matches = re.findall(nav_pattern, content)
    
    nav_dict = {}
    for match in nav_matches:
        nav_id, base_name = match
        if base_name != 'index':
            nav_dict[base_name] = nav_id

    # 3. Unione dei dati e creazione lista finale
    final_pois = []
    for poi_id, data in locations_dict.items():
        nav_id = nav_dict.get(poi_id, f"nav{poi_id.capitalize()}")
        
        poi_entry = {
            "id": data["id"],
            "lat": data["lat"],
            "lon": data["lon"],
            "visual_lat": data["visual_lat"],
            "visual_lon": data["visual_lon"],
            "threshold": data["threshold"],
            "nav_id": nav_id,
            "base_name": poi_id,
            "categoria": data["categoria"]
        }
        final_pois.append(poi_entry)

    # 4. Scrittura del file JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"pois": final_pois}, f, indent=2, ensure_ascii=False)
    
    print(f"Successo: Estratti {len(final_pois)} POI in {output_file}")

if __name__ == "__main__":
    extract_config_from_js()