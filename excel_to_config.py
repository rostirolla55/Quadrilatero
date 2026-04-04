import pandas as pd
import json
import os


def generate_json_from_excel():
    # 1. Configurazione nomi file
    excel_input = "gestione_coordinate_pois.xlsx"
    json_output = "pois_config.json"

    # Controllo se l'invio esiste per evitare errori bloccanti
    if not os.path.exists(excel_input):
        print(
            f"Errore: Il file '{excel_input}' non è stato trovato nella cartella corrente."
        )
        return

    print(f"Lettura di {excel_input}...")

    # 2. Caricamento dati
    # Legge il file Excel (richiede openpyxl installato)
    df = pd.read_excel(excel_input)

    # Pulizia dati: sostituisce i valori vuoti (NaN) con 0 per i calcoli
    df["spost_lat"] = df["spost_lat"].fillna(0)
    df["spost_lon"] = df["spost_lon"].fillna(0)

    pois_list = []

    # 3. Elaborazione righe
    for index, row in df.iterrows():
        # Forza il calcolo delle coordinate visuali sommando i delta
        # Questo risolve il problema del valore visual che rimaneva uguale al base
        v_lat = float(row["lat"]) + float(row["spost_lat"])
        v_lon = float(row["lon"]) + float(row["spost_lon"])

        # AGGIORNAMENTO DEL DATAFRAME: scriviamo i risultati nelle colonne visual
        df.at[index, "visual_lat"] = v_lat
        df.at[index, "visual_lon"] = v_lon

        # ... (creazione dell'oggetto poi per il JSON)
        poi = {
            "id": str(row["id"]),
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "visual_lat": v_lat,
            "visual_lon": v_lon,
            "threshold": int(row["threshold"]) if "threshold" in df.columns else 50,
            "nav_id": (
                str(row["nav_id"])
                if "nav_id" in df.columns
                else f"nav{str(row['id']).capitalize()}"
            ),
            "base_name": str(row["id"]),
            "categoria": (
                str(row["categoria"]) if "categoria" in df.columns else "edificio"
            ),
        }
        pois_list.append(poi)

    # 4. Scrittura del file JSON
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump({"pois": pois_list}, f, indent=2, ensure_ascii=False)

    # 5. NOVITÀ: Salva il DataFrame aggiornato anche sull'Excel
    df.to_excel(excel_input, index=False)
    print(f"Excel '{excel_input}' aggiornato con i nuovi valori visual.")

    print(f"Successo! Il file '{json_output}' è stato generato correttamente.")
    print(f"Processati {len(pois_list)} punti di interesse.")


# --- QUESTA RIGA È FONDAMENTALE PER FAR PARTIRE LO SCRIPT ---
if __name__ == "__main__":
    generate_json_from_excel()
