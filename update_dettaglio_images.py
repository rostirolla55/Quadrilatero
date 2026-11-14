import sys
import os
import json
import zipfile
import xml.etree.ElementTree as ET
import re

def extract_ordered_images_from_docx(docx_path):
    """Legge il DOCX ed estrae i nomi dei file immagine associati a [SPLIT_BLOCK: ...] nell'ordine esatto di apparizione."""
    if not os.path.exists(docx_path):
        return []
    ordered_images = []
    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            xml_content = z.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        full_text = "".join(tree.itertext())
        matches = re.findall(r'\[SPLIT_BLOCK:\s*([^\]]+?)\s*\]', full_text)
        for m in matches:
            clean_name = os.path.basename(m.strip())
            if clean_name and clean_name not in ordered_images:
                ordered_images.append(clean_name)
    except Exception as e:
        print(f"Attenzione lettura DOCX per ordine immagini: {e}")
    return ordered_images

def main():
    if len(sys.argv) < 3:
        print("Uso: python update_dettaglio_images.py <lang> <page_id>")
        sys.exit(1)

    lang = sys.argv[1].lower()
    page_id = sys.argv[2]

    config_path = os.path.join("text_files", f"page_config_{lang}_{page_id}.json")
    if not os.path.exists(config_path):
        print(f"ERRORE: File {config_path} non trovato.")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Cerca prima il DOCX nella lingua corrente, poi fallback su quello italiano
    docx_candidates = [
        os.path.join("DOCS_DA_CONVERTIRE", f"{page_id}_dettaglio_{lang}.docx"),
        os.path.join("DOCS_DA_CONVERTIRE", f"{page_id}_dettaglio_it.docx")
    ]
    ordered_imgs = []
    for candidate in docx_candidates:
        if os.path.exists(candidate):
            ordered_imgs = extract_ordered_images_from_docx(candidate)
            if ordered_imgs:
                break

    img_dir = os.path.join("Assets", "images", page_id, "dettaglio")
    valid_imgs = []

    if ordered_imgs:
        for img_name in ordered_imgs:
            if os.path.exists(os.path.join(img_dir, img_name)):
                valid_imgs.append(f"{page_id}/dettaglio/{img_name}")
    elif os.path.exists(img_dir):
        for fname in sorted(os.listdir(img_dir)):
            if os.path.isfile(os.path.join(img_dir, fname)) and fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                valid_imgs.append(f"{page_id}/dettaglio/{fname}")

    for i in range(1, 6):
        config[f"imageDett{i}"] = valid_imgs[i - 1] if i <= len(valid_imgs) else ""

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    print(f"Aggiornato {config_path} con {len(valid_imgs)} immagini di dettaglio nell'ordine del DOCX: {valid_imgs}")

if __name__ == "__main__":
    main()