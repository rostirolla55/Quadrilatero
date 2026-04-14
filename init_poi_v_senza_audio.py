import json
import os
import re

def clean_coordinates(input_str):
    """Estrae latitudine e longitudine da una stringa (es. da Google Maps)"""
    # Cerca coppie di numeri decimali
    coords = re.findall(r"[-+]?\d*\.\d+|\d+", input_str)
    if len(coords) >= 2:
        return {"lat": coords[0], "lng": coords[1]}
    return None

def initialize_poi():
    print("=== Configurazione Nuovo Punto di Interesse (POI) ===")
    
    # 1. Identificativo Pagina
    poi_id = input("\nInserisci l'ID della pagina (es. chiesa-san-carlo): ").strip().lower()
    if not poi_id:
        print("Errore: L'ID è obbligatorio.")
        return

    # 2. Gestione Coordinate Google Maps
    print(f"\n--- Gestione GPS per {poi_id} ---")
    print("Vai su Google Maps, clicca col tasto destro sul punto e copia le coordinate.")
    gps_input = input("Incolla qui le coordinate (o l'URL di Maps): ")
    
    coords = clean_coordinates(gps_input)
    if not coords:
        print("❌ Errore: Non sono riuscito a trovare coordinate valide.")
        return
    
    print(f"✅ Coordinate identificate: Lat {coords['lat']}, Lng {coords['lng']}")

    # 3. Creazione cartelle di supporto
    paths = [
        f"public/audio/{poi_id}",
        "DOCS_DA_CONVERTIRE"
    ]
    
    for path in paths:
        os.makedirs(path, exist_ok=True)
    
    # 4. Aggiornamento pois_config.json
    config_file = 'pois_config.json'
    
    # Carica il file esistente o crealo se vuoto
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Aggiungi o aggiorna il POI
    data[poi_id] = {
        "id": poi_id,
        "coords": [float(coords['lat']), float(coords['lng'])],
        "image": f"/images/{poi_id}.jpg",
        "audioDir": f"/audio/{poi_id}/"
    }

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Configurazione completata per '{poi_id}'!")
    print(f"📂 Cartelle create. File '{config_file}' aggiornato.")
    print(f"👉 Ora puoi mettere il file Word in 'DOCS_DA_CONVERTIRE/{poi_id}.docx'")

if __name__ == "__main__":
    initialize_poi()