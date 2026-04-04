import json
import pandas as pd

def update_json_from_excel(excel_path, json_path):
    df = pd.read_excel(excel_path)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    is_dict = isinstance(data, dict)
    pois_list = data['pois'] if is_dict else data

    # Creiamo il mapping dall'Excel
    excel_data = df.set_index('id').to_dict('index')

    for poi in pois_list:
        poi_id = poi.get('id')
        if poi_id in excel_data:
            row = excel_data[poi_id]
            
            # LOGICA: Visual = Reale (fisso) + Spostamento (modificabile nell'Excel)
            # Questo permette di modificare 'spost_lat' nell'Excel e aggiornare il JSON
            new_visual_lat = poi['lat'] + row['spost_lat']
            new_visual_lon = poi['lon'] + row['spost_lon']
            
            poi['visual_lat'] = round(new_visual_lat, 6)
            poi['visual_lon'] = round(new_visual_lon, 6)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Aggiornamento completato: visual_lat e visual_lon ricalcolati in {json_path}")

if __name__ == "__main__":
    update_json_from_excel('gestione_coordinate_pois.xlsx', 'pois_config.json')