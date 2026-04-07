import geopandas as gpd
import pandas as pd
import json
import matplotlib.pyplot as plt

def process_and_verify(input_file, output_file):
    # 1. Caricamento dati originali
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. Pulizia: usiamo solo i dati reali 'lat' e 'lon'
    df = pd.DataFrame(data['pois'])
    columns_to_keep = ['id', 'lat', 'lon', 'threshold', 'nav_id', 'base_name', 'categoria']
    df_clean = df[columns_to_keep].copy()

    # 3. Creazione GeoDataFrame per la validazione spaziale
    gdf = gpd.GeoDataFrame(
        df_clean, 
        geometry=gpd.points_from_xy(df_clean.lon, df_clean.lat), 
        crs="EPSG:4326"
    )

    # 4. Generazione Anteprima Visiva
    # Questo ti permette di vedere la disposizione dei pin su un grafico
    ax = gdf.plot(figsize=(10, 10), color='red', marker='o', markersize=50)
    for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf.id):
        ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points", fontsize=8)
    
    plt.title("Anteprima Posizionamento Pin - Sito Turistico")
    plt.xlabel("Longitudine")
    plt.ylabel("Latitudine")
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Salva l'anteprima come immagine
    plt.savefig('anteprima_mappa.png')
    print("Anteprima salvata come 'anteprima_mappa.png'.")

    # 5. Salvataggio del nuovo pois_config.json pulito
    clean_dict = {"pois": df_clean.to_dict(orient='records')}
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_dict, f, indent=2, ensure_ascii=False)
    
    print(f"File finale salvato con successo in: {output_file}")

# Esecuzione
process_and_verify('pois_config.json', 'pois_config_fixed.json')