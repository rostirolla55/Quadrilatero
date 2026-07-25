import sys
import os
import re
from docx import Document
from PIL import Image
from io import BytesIO

# --- CONFIGURAZIONI ---
DOCX_DIR = "DOCS_DA_CONVERTIRE"
ASSETS_BASE_DIR = "Assets/images"

# Pattern per identificare il marker e catturare il nome del file desiderato
SPLIT_BLOCK_PATTERN = r'\[SPLIT_BLOCK:\s*(.+?\.(?:jpg|jpeg|png|gif|bmp))\]'

def get_target_filename(paragraph):
    """Estrae il nome del file immagine dal marker [SPLIT_BLOCK]"""
    match = re.search(SPLIT_BLOCK_PATTERN, paragraph.text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_images_sequentially(document):
    """
    Scansiona il documento in ordine di lettura top-to-bottom e
    collega ciascuna immagine trovata nei paragrafi al marker [SPLIT_BLOCK] successivo.
    """
    pairs = [] # Lista di tuple: (target_filename, image_bytes)
    pending_image_bytes = None

    for p in document.paragraphs:
        # 1. Cerca se nel paragrafo c'è un'immagine (elemento blip XML)
        for r in p._p.xpath('.//a:blip'):
            embed_id = r.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            if embed_id and embed_id in document.part.rels:
                image_part = document.part.rels[embed_id].target_part
                pending_image_bytes = image_part.blob

        # 2. Cerca se nel paragrafo c'è il marker [SPLIT_BLOCK]
        target_filename = get_target_filename(p)
        if target_filename and pending_image_bytes:
            pairs.append((target_filename, pending_image_bytes))
            pending_image_bytes = None # Reset per la prossima immagine

    return pairs

def extract_images_from_docx(page_id, docx_filename):
    normalized_page_id = page_id.lower()

    docx_path = os.path.join(DOCX_DIR, docx_filename)
    if not os.path.exists(docx_path):
        print(f"ERRORE: File DOCX non trovato: {docx_path}", file=sys.stderr)
        return False, 0, 0

    output_dir = os.path.join(ASSETS_BASE_DIR, normalized_page_id)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Directory di output creata: {output_dir}")

    try:
        document = Document(docx_path)
    except Exception as e:
        print(f"ERRORE: Impossibile aprire il documento DOCX '{docx_path}': {e}", file=sys.stderr)
        return False, 0, 0

    # Estrazione sequenziale ordinata top-to-bottom
    image_pairs = extract_images_sequentially(document)
    markers_found = len(image_pairs)

    print(f"Numero di coppie (Immagine + [SPLIT_BLOCK]) trovate in ordine sequenziale: {markers_found}")

    extracted_count = 0

    for target_filename, image_bytes in image_pairs:
        try:
            output_path = os.path.join(output_dir, target_filename)

            with Image.open(BytesIO(image_bytes)) as img:
                img.save(output_path, format=img.format if not target_filename.lower().endswith('.jpg') else 'jpeg')

            print(f"-> Immagine estratta e salvata correttamente: {output_path}")
            extracted_count += 1
        except Exception as e:
            print(f"ERRORE durante il salvataggio dell'immagine {target_filename}: {e}", file=sys.stderr)

    print(f"\nEstrazione immagini completata. Estratte {extracted_count} immagini.")
    return True, markers_found, extracted_count

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python extract_images.py [ID_pagina] [nome_file_docx]", file=sys.stderr)
        sys.exit(1)

    PAGE_ID = sys.argv[1]
    DOCX_FILE = sys.argv[2]

    success, markers, extracted = extract_images_from_docx(PAGE_ID, DOCX_FILE)

    if success and markers == extracted and extracted > 0:
        sys.exit(0)
    elif success and markers != extracted:
        print(f"ATTENZIONE: Trovati {markers} marker ma estratte {extracted} immagini.", file=sys.stderr)
        sys.exit(1)
    else:
        sys.exit(1)