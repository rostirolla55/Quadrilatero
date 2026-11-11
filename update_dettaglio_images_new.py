import sys
import json
import os
import glob

def update_images(lang, page_id):
    config_path = f"data/config/page_config_{lang}_{page_id}.json"
    img_dir = f"Assets/images/{page_id}/dettaglio"
    
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # 1. Prende SOLO i file salvati nella sottocartella dettaglio
    imgs = []
    if os.path.exists(img_dir):
        imgs = sorted([
            os.path.basename(f) for f in glob.glob(f"{img_dir}/*.*")
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ])

    # 2. Carica il config esistente se c'è
    data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}

    # 3. RESET RIGIDO: sovrascrive interamente le chiavi imageDett1..5
    for i in range(5):
        key = f"imageDett{i+1}"
        if i < len(imgs):
            data[key] = f"{page_id}/dettaglio/{imgs[i]}"
        else:
            data[key] = ""

    # 4. Salva il file di config pulito
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Config {config_path} resettato ed ereditati {len(imgs)} file da {img_dir}.")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        update_images(sys.argv[1], sys.argv[2])