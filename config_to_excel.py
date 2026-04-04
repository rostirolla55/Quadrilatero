import json
import pandas as pd

def extract_to_excel(json_path, excel_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Se il JSON ha una chiave radice (es. 'pois'), adattare qui
    pois = data if isinstance(data, list) else data.get('pois', [])
    
    rows = []
    for poi in pois:
        lat = poi.get('lat', 0)
        lon = poi.get('lon', 0)
        v_lat = poi.get('visual_lat', lat)
        v_lon = poi.get('visual_lon', lon)
        
        rows.append({
            'id': poi.get('id'),
            'lat': lat,
            'spost_lat': round(v_lat - lat, 6),
            'visual_lat': v_lat,
            'lon': lon,
            'spost_lon': round(v_lon - lon, 6),
            'visual_lon': v_lon
        })
    
    df = pd.DataFrame(rows)
    df.to_excel(excel_path, index=False)
    print(f"File Excel creato con successo: {excel_path}")

if __name__ == "__main__":
    extract_to_excel('pois_config.json', 'gestione_coordinate_pois.xlsx')