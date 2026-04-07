import json

def pulizia_completa_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    nuovi_pois = []
    for p in data['pois']:
        # Ricostruiamo il POI con TUTTE le chiavi corrette
        pulito = {
            "id": p.get("id"),
            "lat": p.get("lat"),
            "lon": p.get("lon"),
            "threshold": p.get("threshold", 50), # Conserviamo il threshold
            "nav_id": p.get("nav_id"),
            "base_name": p.get("base_name"),
            "categoria": p.get("categoria")
        }
        nuovi_pois.append(pulito)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({"pois": nuovi_pois}, f, indent=2, ensure_ascii=False)
    
    print("Successo: pois_config.json aggiornato con threshold e coordinate pulite.")

pulizia_completa_config('pois_config.json')