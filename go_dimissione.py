import os
import json
import sys
import glob

def go_dimissione(page_name):
    """
    Procedura completa di dimissione di una pagina.
    - Rimuove dai JSON in menu_json/
    - Rimuove dai JSON in data/translations/{lang}/texts.json
    - Rimuove dai JSON in pois_config.json
    - Rimuove file fisici (Audio e Frammenti)
    - Genera .bat di aggiornamento
    """
    languages = ['it', 'en', 'fr', 'es']
    menu_folder = os.path.join(os.getcwd(), "menu_json")
    trans_folder = os.path.join(os.getcwd(), "data", "translations")
    batch_filename = "dimissione_procedura.bat"
    
    print(f"--- Inizio procedura di dimissione per: {page_name} ---")

    # 1. Pulizia dei file nav-*.json (Menu)
    for lang in languages:
        nav_file = os.path.join(menu_folder, f"nav-{lang}.json")
        if os.path.exists(nav_file):
            try:
                with open(nav_file, 'r', encoding='utf-8') as f:
                    nav_data = json.load(f)
                
                is_dict = isinstance(nav_data, dict)
                items = nav_data.get('items', []) if is_dict else nav_data
                
                original_len = len(items)
                new_items = [
                    item for item in items 
                    if page_name.lower() not in item.get('id', '').lower() and 
                       page_name.lower() not in item.get('href', '').lower()
                ]
                
                if len(new_items) < original_len:
                    if is_dict: nav_data['items'] = new_items
                    else: nav_data = new_items
                    with open(nav_file, 'w', encoding='utf-8') as f:
                        json.dump(nav_data, f, ensure_ascii=False, indent=4)
                    print(f"OK: Rimosso dal menu {lang}")
            except Exception as e:
                print(f"Errore su {nav_file}: {e}")

    # 2. Pulizia di texts.json (Frammenti e Audio references)
    for lang in languages:
        texts_file = os.path.join(trans_folder, lang, "texts.json")
        if os.path.exists(texts_file):
            try:
                with open(texts_file, 'r', encoding='utf-8') as f:
                    texts_data = json.load(f)
                
                if page_name in texts_data:
                    del texts_data[page_name]
                    with open(texts_file, 'w', encoding='utf-8') as f:
                        json.dump(texts_data, f, ensure_ascii=False, indent=4)
                    print(f"OK: Rimosso {page_name} da {texts_file}")
                else:
                    print(f"Info: {page_name} non presente in {texts_file}")
            except Exception as e:
                print(f"Errore su {texts_file}: {e}")

    # 3. Modifica di pois_config.json
    poi_file = "pois_config.json"
    if os.path.exists(poi_file):
        try:
            with open(poi_file, 'r', encoding='utf-8') as f:
                poi_data = json.load(f)
            if "pois" in poi_data:
                original_count = len(poi_data["pois"])
                poi_data["pois"] = [p for p in poi_data["pois"] if p.get('base_name') != page_name]
                if len(poi_data["pois"]) < original_count:
                    with open(poi_file, 'w', encoding='utf-8') as f:
                        json.dump(poi_data, f, ensure_ascii=False, indent=4)
                    print(f"OK: Rimosso POI da {poi_file}")
        except Exception as e:
            print(f"Errore su {poi_file}: {e}")

    # 4. Rimozione fisica Audio e Frammenti
    print("\n--- Rimozione file fisici ---")
    audio_base = os.path.join("Assets", "Audio")
    for lang in languages:
        # Audio
        audio_path = os.path.join(audio_base, lang, f"{page_name}.mp3")
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"Cancellato audio: {audio_path}")
        
        # Frammenti HTML
        pattern = f"{lang}_{page_name}_maintext*.html"
        for frag in glob.glob(pattern):
            os.remove(frag)
            print(f"Cancellato frammento: {frag}")

    # 5. Creazione del file .bat
    try:
        with open(batch_filename, 'w', encoding='utf-8') as bat:
            bat.write("@echo off\n")
            bat.write(f"echo --- PULIZIA E SINCRONIZZAZIONE PER {page_name} ---\n")
            bat.write(f"del /Q {page_name}.html 2>nul\n")
            for lang in languages:
                bat.write(f"del /Q {page_name}-{lang}.html 2>nul\n")
            bat.write("python update_html_from_json.py\n")
            bat.write("python load_config_poi.py\n")
            bat.write("echo PROCEDURA COMPLETATA.\n")
            bat.write("pause\n")
        print(f"\nProcedura Batch generata: {batch_filename}")
    except Exception as e:
        print(f"Errore creazione batch: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        target = input("Nome pagina (es. chiesasancarlo): ").strip()
    else:
        target = sys.argv[1]
    
    if target:
        go_dimissione(target)