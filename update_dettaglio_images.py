import sys
import json
import os
import glob

def update_dettaglio_config(lang, page_id):
    config_path = f"text_files/page_config_{lang}_{page_id}.json"
    img_dir = f"Assets/images/{page_id}/dettaglio"
    text_files_dir = "text_files"
    
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # 1. Carica il file JSON di configurazione esistente in text_files
    data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}

    # 2. Scansione Immagini di Dettaglio (Assets/images/{page_id}/dettaglio/*.*)
    imgs = []
    if os.path.exists(img_dir):
        imgs = sorted([
            os.path.basename(f) for f in glob.glob(f"{img_dir}/*.*")
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ])

    for i in range(5):
        key = f"imageDett{i+1}"
        if i < len(imgs):
            data[key] = f"{page_id}/dettaglio/{imgs[i]}"
        else:
            data[key] = ""

    # 3. Scansione Frammenti di Testo Dettaglio (text_files/{lang}_{page_id}_dettText*.html)
    dett_texts = sorted([
        os.path.basename(f) for f in glob.glob(f"{text_files_dir}/{lang}_{page_id}_dettText*.html")
    ])

    for i in range(5):
        key = f"dettText{i+1}"
        if i < len(dett_texts):
            data[key] = dett_texts[i]
        else:
            data[key] = ""

    # 4. Salvataggio del file di configurazione completo
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Config {config_path} aggiornato: trovate {len(imgs)} immagini e {len(dett_texts)} frammenti dettText.")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        update_dettaglio_config(sys.argv[1], sys.argv[2])