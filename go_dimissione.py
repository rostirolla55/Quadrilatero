import os
import json
import sys
import glob
import shutil

def go_dimissione(page_name):
    """
    Procedura RADICALE di dimissione di una pagina.
    Pulisce JSON, navigazione, GPS, file audio, immagini, documenti e frammenti HTML.
    """
    languages = ['it', 'en', 'fr', 'es']
    root = os.getcwd()
    
    # Percorsi cartelle
    menu_folder = os.path.join(root, "menu_json")
    trans_folder = os.path.join(root, "data", "translations")
    docs_folder = os.path.join(root, "DOCS_DA_CONVERTIRE")
    text_files_folder = os.path.join(root, "text_files")
    images_base = os.path.join(root, "Assets", "images")
    audio_base = os.path.join(root, "Assets", "audio")
    
    # ID Menu (es. navChiesaSanCarlo)
    nav_id_to_remove = f"nav{page_name[0].upper()}{page_name[1:]}"
    
    print(f"--- AVVIO DISMISSIONE TOTALE: {page_name} ---")

    # 1. Pulizia dei file nav-*.json (Menu Strutturale)
    for lang in languages:
        nav_file = os.path.join(menu_folder, f"nav-{lang}.json")
        if os.path.exists(nav_file):
            try:
                with open(nav_file, 'r', encoding='utf-8') as f:
                    nav_data = json.load(f)
                
                is_dict = isinstance(nav_data, dict)
                items = nav_data.get('items', []) if is_dict else nav_data
                
                new_items = [
                    item for item in items 
                    if page_name.lower() not in item.get('id', '').lower() and 
                       page_name.lower() not in item.get('href', '').lower()
                ]
                
                if len(new_items) != len(items):
                    if is_dict: nav_data['items'] = new_items
                    else: nav_data = new_items
                    with open(nav_file, 'w', encoding='utf-8') as f:
                        json.dump(nav_data, f, ensure_ascii=False, indent=4)
                    print(f"OK: Rimosso dal menu strutturale {lang}")
            except Exception as e: print(f"Errore su {nav_file}: {e}")

    # 2. Pulizia di texts.json (Contenuti e Nav Label)
    for lang in languages:
        texts_file = os.path.join(trans_folder, lang, "texts.json")
        if os.path.exists(texts_file):
            try:
                with open(texts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                modified = False
                if page_name in data:
                    del data[page_name]
                    modified = True
                if "nav" in data and nav_id_to_remove in data["nav"]:
                    del data["nav"][nav_id_to_remove]
                    modified = True
                if modified:
                    with open(texts_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    print(f"OK: Pulito texts.json ({lang})")
            except Exception as e: print(f"Errore su {texts_file}: {e}")

    # 3. Pulizia pois_config.json (GPS)
    poi_file = "pois_config.json"
    if os.path.exists(poi_file):
        try:
            with open(poi_file, 'r', encoding='utf-8') as f:
                p_data = json.load(f)
            if "pois" in p_data:
                orig = len(p_data["pois"])
                p_data["pois"] = [p for p in p_data["pois"] if p.get('base_name') != page_name]
                if len(p_data["pois"]) < orig:
                    with open(poi_file, 'w', encoding='utf-8') as f:
                        json.dump(p_data, f, ensure_ascii=False, indent=4)
                    print(f"OK: Rimosso POI da {poi_file}")
        except Exception as e: print(f"Errore su {poi_file}: {e}")

    # 4. RIMOZIONE FILE FISICI (Il tuo report dir /s)
    print("\n--- Pulizia File Fisici ---")

    # A. Frammenti HTML in /text_files/
    # Cerchiamo pattern come "it_chiesasancarlo_maintext1.html"
    if os.path.exists(text_files_folder):
        for lang in languages:
            pattern = os.path.join(text_files_folder, f"{lang}_{page_name}_*.html")
            for f in glob.glob(pattern):
                os.remove(f)
                print(f"Rimosso frammento: {os.path.basename(f)}")

    # B. Documenti DOCX in DOCS_DA_CONVERTIRE
    if os.path.exists(docs_folder):
        # Match case insensitive per "ChiesaSanCarlo" o "chiesasancarlo"
        for f_name in os.listdir(docs_folder):
            if page_name.lower() in f_name.lower() and f_name.endswith(".docx"):
                os.remove(os.path.join(docs_folder, f_name))
                print(f"Rimosso documento sorgente: {f_name}")

    # C. Cartella Immagini
    img_dir = os.path.join(images_base, page_name)
    if os.path.exists(img_dir):
        shutil.rmtree(img_dir)
        print(f"Rossa intera cartella immagini: {img_dir}")

    # D. Audio e file TXT associati
    for lang in languages:
        # File MP3
        audio_file = os.path.join(audio_base, lang, f"{page_name}.mp3")
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"Rimosso audio: {audio_file}")
        # Sottocartella testo_audio se esiste
        txt_audio = os.path.join(audio_base, lang, "testo_audio", f"{page_name}.txt")
        if os.path.exists(txt_audio):
            os.remove(txt_audio)
            print(f"Rimosso testo audio: {txt_audio}")

    # E. File Batch orfani (add_*.bat)
    for bat_file in glob.glob(f"add_{page_name}.bat"):
        os.remove(bat_file)
        print(f"Rimosso script batch orfano: {bat_file}")

    # 5. Generazione Batch di Sincronizzazione Finale
    batch_fn = "dimissione_sincronizza.bat"
    with open(batch_fn, 'w', encoding='utf-8') as bat:
        bat.write("@echo off\n")
        bat.write(f"echo --- ELIMINAZIONE FILE HTML GENERATI PER {page_name} ---\n")
        bat.write(f"del /Q {page_name}.html 2>nul\n")
        for lang in languages:
            bat.write(f"del /Q {page_name}-{lang}.html 2>nul\n")
        bat.write("echo --- RIGENERAZIONE MAIN.JS E ALTRE PAGINE ---\n")
        bat.write("python update_html_from_json.py\n")
        bat.write("python load_config_poi.py\n")
        bat.write("echo PROCEDURA COMPLETATA CON SUCCESSO.\n")
        bat.write("pause\n")
    
    print(f"\nFine procedura. Esegui '{batch_fn}' per pulire gli HTML finali.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else input("Nome pagina: ").strip()
    if target: go_dimissione(target)