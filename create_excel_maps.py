import json
import pandas as pd

# 1. Caricamento dei file
with open('pois_config.json', 'r', encoding='utf-8') as f:
    pois_data = json.load(f)

with open('texts.json', 'r', encoding='utf-8') as f:
    texts_data = json.load(f)

# 2. Estrazione titoli dal blocco nav (italiano)
nav_titles = texts_data.get("nav", {})

# URL base fornito
BASE_URL = "https://rostirolla55.github.io/Quadrilatero/"

excel_data = []

# --- NUOVA LOGICA: Dizionario per gestire le sovrapposizioni ---
# Serve per contare quante volte incontriamo le stesse coordinate
coordinata_count = {}

# Valore dell'offset: circa 4-5 metri per ogni passo (0.00004 gradi)
OFFSET_STEP = 0.00004 

for poi in pois_data['pois']:
    nav_id = poi.get('nav_id')
    
    # Recupero il titolo
    titolo_poi = nav_titles.get(nav_id, poi.get('id').capitalize())
    
    # Coordinate originali arrotondate a 6 decimali per uniformità
    lat_orig = round(float(poi.get("lat")), 6)
    lon_orig = round(float(poi.get("lon")), 6)
    
    # Creiamo una chiave unica per identificare la posizione
    pos_key = (lat_orig, lon_orig)
    
    # Determiniamo quante volte abbiamo già visto questa posizione
    count = coordinata_count.get(pos_key, 0)
    
    # Applichiamo lo spostamento sequenziale: 
    # Il primo punto (count=0) resta originale, i successivi si spostano
    lat_map = lat_orig + (count * OFFSET_STEP)
    lon_map = lon_orig + (count * OFFSET_STEP)
    
    # Aggiorniamo il contatore per la prossima occorrenza
    coordinata_count[pos_key] = count + 1
    
    # Costruzione del link
    poi_id = poi.get('id')
    link_pagina = f"{BASE_URL}{poi_id}.html"
    
    # Creazione della riga
    row = {
        "Punto di Interesse": titolo_poi,
        "Latitudine": lat_map,
        "Longitudine": lon_map,
        "Sito Web": link_pagina,
        "Info": "Seleziona il link per aprire la scheda storica e l'audio guida."
    }
    excel_data.append(row)

# 3. Generazione del file Excel
df = pd.DataFrame(excel_data)
output_name = "Import_MyMaps_Bologna.xlsx"
df.to_excel(output_name, index=False)

print(f"File '{output_name}' creato correttamente.")
print(f"Gestiti {len(excel_data)} punti. Le sovrapposizioni (come Pioggia 1, 2, 3) sono state distanziate sequenzialmente.")