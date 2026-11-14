import os
import sys
from docx import Document

def extract_dettaglio_images(docx_path, page_id):
    output_dir = os.path.join("Assets", "images", page_id, "dettaglio")
    os.makedirs(output_dir, exist_ok=True)

    doc = Document(docx_path)
    img_count = 0

    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            img_count += 1
            if img_count > 5:
                break
            img_data = rel.target_part.blob
            out_filename = f"imageDett{img_count}.jpg"
            out_path = os.path.join(output_dir, out_filename)
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"-> Estratta immagine dettaglio: {out_path}")

    return img_count

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python extract_images_dettaglio.py <percorso_docx> <page_id>")
        sys.exit(1)
    extract_dettaglio_images(sys.argv[1], sys.argv[2])