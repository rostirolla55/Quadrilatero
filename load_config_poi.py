# -*- coding: utf-8 -*-
import json
import os
import re

# ===========================================
# CONFIGURAZIONE DEI CAMPI DI DETTAGLIO DEFAULT
# ===========================================
CAMPI_DETTAGLIO_DEFAULT = {
    "dettText1": "",
    "dettText2": "",
    "dettText3": "",
    "dettText4": "",
    "dettText5": "",
    "imageDett1": "",
    "imageDett2": "",
    "imageDett3": "",
    "imageDett4": "",
    "imageDett5": ""
}

def arricchisci_texts_json_con_dettagli(percorso_json, lang):
    """
    Scansiona data/translations/{lang}/texts.json e aggiunge le chiavi dettText e imageDett 
    vuote ("") ai POI che ne sono sprovvisti, preservando i dati esistenti.
    """
    if not os.path.exists(percorso_json):
        return

    with open(percorso_json, 'r', encoding='utf-8') as f:
        dati = json.load(f)

    modificato = False
    CHIAVI_ESCLUSE_DETTAGLI = {"nav"}
    for poi_id, poi_data in dati.items():
        if poi_id in CHIAVI_ESCLUSE_DETTAGLI:
            continue
        if isinstance(poi_data, dict):
            for chiave, valore_def in CAMPI_DETTAGLIO_DEFAULT.items():
                if chiave not in poi_data:
                    poi_data[chiave] = ""
                    modificato = True

    if modificato:
        with open(percorso_json, 'w', encoding='utf-8') as f:
            json.dump(dati, f, ensure_ascii=False, indent=4)
        print(f"  ✓ Sincronizzati campi dettaglio (vuoti) in: {percorso_json}")
        
def update_main_js():
    config_file = "pois_config.json"
    js_file = "main.js"

    if not os.path.exists(config_file) or not os.path.exists(js_file):
        print("Errore: Uno dei file non è presente nella cartella.")
        return

    # 1. Caricamento dati dal JSON
    with open(config_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pois = data.get("pois", [])

    # 2. Generazione stringa POIS_LOCATIONS (include categoria, distanceThreshold e ordine_cammino)
    pois_locations_js = "const POIS_LOCATIONS = [\n"
    for i, p in enumerate(pois):
        comma = "," if i < len(pois) - 1 else ""
        categoria = p.get('categoria', 'edificio')

        # Gestione del campo ordine_cammino (opzionale)
        ordine_cammino_str = ""
        if "ordine_cammino" in p and p["ordine_cammino"] is not None:
            ordine_cammino_str = f", ordine_cammino: {p['ordine_cammino']}"

        pois_locations_js += (
            f"  {{ id: '{p['id']}', lat: {p['lat']}, lon: {p['lon']}, "
            f"distanceThreshold: {p['threshold']}, categoria: '{categoria}'{ordine_cammino_str} }}{comma}\n"
        )
    pois_locations_js += "];"

    # 3. Generazione stringa navLinksData (include poiId per il menu dinamico)
    nav_links_js = "const navLinksData = [\n"
    nav_links_js += "  { id: 'navHome', key: 'navHome', base: 'index', poiId: 'home' },\n"
    for i, p in enumerate(pois):
        comma = "," if i < len(pois) - 1 else ""
        nav_links_js += (
            f"  {{ id: '{p['nav_id']}', key: '{p['nav_id']}', "
            f"base: '{p['base_name']}', poiId: '{p['id']}' }}{comma}\n"
        )
    nav_links_js += "];"

    # 4. Lettura e Sostituzione nel file main.js
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Sostituzione del blocco POIS_LOCATIONS
    content = re.sub(r'const POIS_LOCATIONS = \[.*?\];', pois_locations_js, content, flags=re.DOTALL)

    # Sostituzione del blocco navLinksData
    content = re.sub(r'const navLinksData = \[.*?\];', nav_links_js, content, flags=re.DOTALL)

    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✓ main.js aggiornato con successo: POIS_LOCATIONS e navLinksData allineati a pois_config.json.")

    # 5. Sincronizzazione automatica dei campi dettaglio nei file texts.json (it, en, fr, es)
    for lang in ['it', 'en', 'fr', 'es']:
        percorso_texts = os.path.join("data", "translations", lang, "texts.json")
        arricchisci_texts_json_con_dettagli(percorso_texts, lang)

if __name__ == "__main__":
    update_main_js()