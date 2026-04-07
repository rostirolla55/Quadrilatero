import re
import json

def extract_config_from_js():
    js_file = "main.js"
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex per estrarre esattamente: id, lat, lon, distanceThreshold, categoria
    poi_pattern = r"\{\s*id:\s*'([^']*)',\s*lat:\s*([\d\.]+),\s*lon:\s*([\d\.]+),\s*distanceThreshold:\s*(\d+),\s*categoria:\s*'([^']*)'\s*\}"
    matches = re.findall(poi_pattern, content)
    
    final_pois = []
    for m in matches:
        poi_id = m[0]
        final_pois.append({
            "id": poi_id,
            "lat": float(m[1]),
            "lon": float(m[2]),
            "threshold": int(m[3]),
            "categoria": m[4],
            "nav_id": f"nav{poi_id.capitalize()}",
            "base_name": poi_id
        })

    with open("pois_config.json", "w", encoding="utf-8") as f:
        json.dump({"pois": final_pois}, f, indent=2, ensure_ascii=False)
    print("✓ pois_config.json rigenerato correttamente.")