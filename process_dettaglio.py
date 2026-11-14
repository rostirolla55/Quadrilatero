import os
import sys
import json
from bs4 import BeautifulSoup

def update_dettaglio_json_and_fragments(raw_html_path, lang, page_id):
    with open(raw_html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    body_html = "".join(str(tag) for tag in soup.body.contents) if soup.body else str(soup)
    blocks = [b.strip() for b in body_html.split("[SPLIT_BLOCK]") if b.strip()]

    # 1. Generazione frammenti dettText1..5 (in root e in text_files)
    os.makedirs("text_files", exist_ok=True)
    dett_text_keys = {}

    for i in range(1, 6):
        key_name = f"dettText{i}"
        if i <= len(blocks):
            frag_filename = f"{lang}_{page_id}_dettText{i}.html"
            dett_text_keys[key_name] = frag_filename

            # Salva nella root (dove fetch() di main.js li carica) e in text_files
            for folder in [".", "text_files"]:
                with open(os.path.join(folder, frag_filename), "w", encoding="utf-8") as out_f:
                    out_f.write(blocks[i - 1])
        else:
            dett_text_keys[key_name] = ""

    # 2. Verifica immagini estratte in Assets/images/<page_id>/dettaglio/
    img_dir = os.path.join("Assets", "images", page_id, "dettaglio")
    image_dett_keys = {}

    for i in range(1, 6):
        key_name = f"imageDett{i}"
        img_filename = f"imageDett{i}.jpg"
        if os.path.exists(os.path.join(img_dir, img_filename)):
            image_dett_keys[key_name] = f"{page_id}/dettaglio/{img_filename}"
        else:
            image_dett_keys[key_name] = ""

    # 3. Aggiornamento diretto di data/translations/<lang>/texts.json
    json_path = os.path.join("data", "translations", lang, "texts.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as jf:
            texts_data = json.load(jf)
    else:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        texts_data = {}

    if page_name_block := texts_data.setdefault(page_id, {}):
        pass
    texts_data[page_id].update(dett_text_keys)
    texts_data[page_id].update(image_dett_keys)

    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(texts_data, jf, ensure_ascii=False, indent=4)

    print(f"Aggiornato {json_path} per '{page_id}' con chiavi dettText1..5 e imageDett1..5.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python process_dettaglio.py <raw_html_path> <lang> <page_id>")
        sys.exit(1)
    update_dettaglio_json_and_fragments(sys.argv[1], sys.argv[2], sys.argv[3])