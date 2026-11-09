import re
import json
import sys
import os
from typing import Dict, Tuple

# --- CONFIGURAZIONE GLOBALE ---
TEMP_HTML_FILENAME = "raw_output.html"
OUTPUT_DIR = "text_files"

# --- REGEX PER PULIZIA E SPLIT ---
IMG_TAG_REGEX = re.compile(r'<img[^>]*?>', re.IGNORECASE | re.DOTALL)
SPLIT_BLOCK_CLEANING_REGEX = re.compile(
    r'.*?(\[SPLIT_BLOCK:(.*?)\]).*?',
    re.IGNORECASE | re.DOTALL
)

def get_fragment_prefix(page_id: str) -> str:
    if page_id.lower() == 'home':
        return 'index'
    return page_id

def clean_html_content(html_content: str) -> str:
    """
    Rimuove i tag <img>, pulisce i tag <div> wrapper generati da LibreOffice
    e ripulisce le nuove linee/spazi superflui.
    """
    cleaned = IMG_TAG_REGEX.sub('', html_content)
    
    # 1. Rimuove eventuali tag <div> e </div> (apertura con qualsiasi attributo e chiusura)
    cleaned = re.sub(r'</?div[^>]*>', '', cleaned, flags=re.IGNORECASE)
    
    # 2. Rimuove le doppie nuove righe/spazi e tag <p> e </p> vuoti
    cleaned = re.sub(r'(<p[^>]*>\s*</p>|\n\s*\n)', '\n', cleaned).strip()
    return cleaned

def sanitize_split_markers(html_content: str) -> str:
    print("DEBUG: Pre-pulizia dei marcatori SPLIT...")
    contamination_area_pattern = re.compile(r'\[[^\]]*?SPLIT_BLOCK[^\]]*?\]', re.IGNORECASE | re.DOTALL)
    
    def clean_match(match):
        contaminated_text = match.group(0)
        cleaned_text = re.sub(r'<\/?\w+[^>]*?>', '', contaminated_text)
        return cleaned_text.strip()

    sanitized_content = contamination_area_pattern.sub(clean_match, html_content)
    
    if sanitized_content != html_content:
        print("DEBUG: Trovati e puliti marcatori SPLIT contaminati da HTML.")
    
    return sanitized_content

def process_document(html_input: str, lang: str, page_id: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    page_id_lower = page_id.lower()
    print(f"Inizio Elaborazione e Split: Pagina '{page_id.upper()}', Lingua '{lang}'")

    fragment_file_prefix = get_fragment_prefix(page_id_lower)
    print(f"DEBUG: Prefisso per i nomi dei file frammento: '{fragment_file_prefix}'")

    html_input = sanitize_split_markers(html_input)

    split_token = "---SPLIT-HERE---"
    image_filenames = []
    
    extraction_regex = re.compile(
        r'(<p[^>]*>)?\s*\[SPLIT_BLOCK:(.*?)\]\s*(</p>)?',
        re.IGNORECASE | re.DOTALL
    )

    split_matches = extraction_regex.findall(html_input)
    image_filenames = [match[1].strip() for match in split_matches]

    print(f"\n--- RISULTATO DEBUG REGEX ---")
    print(f"Trovati {len(image_filenames)} nomi file immagine. Lista: {image_filenames}")

    if not image_filenames and '[SPLIT_BLOCK:' in html_input:
        print("ATTENZIONE: Il marker [SPLIT_BLOCK] è presente, ma la REGEX non lo cattura.")
    print("-----------------------------\n")

    content_with_tokens = extraction_regex.sub(split_token, html_input)
    raw_fragments = content_with_tokens.split(split_token)

    print(f"Trovati {len(raw_fragments)} frammenti di testo grezzi prima della pulizia.")
    for i, frag in enumerate(raw_fragments):
        print(f"  Frammento {i+1} (Inizio): {frag[:50].strip()}...")
    print("------------------------------------------------------\n")

    fragments_html = {}
    json_data = {}
    fragment_index = 1

    for i, raw_html in enumerate(raw_fragments):
        cleaned_html = clean_html_content(raw_html)

        if not cleaned_html:
            continue

        main_text_key = f"mainText{fragment_index}"
        file_base_name = main_text_key.lower()
        html_filepath = f"{lang}_{fragment_file_prefix}_{file_base_name}.html" 

        fragments_html[html_filepath] = cleaned_html
        json_data[main_text_key] = html_filepath

        print(f"  - Creato Frammento di Testo {fragment_index}: {html_filepath}")

        image_index = fragment_index - 1

        if image_index < len(image_filenames):
            image_filename = image_filenames[image_index]
            image_source_key = f"imageSource{fragment_index}"
            image_path_value = f"{page_id_lower}/{image_filename}"
            json_data[image_source_key] = image_path_value
            print(f"  - Associato Immagine {fragment_index} al riferimento: {image_path_value}")

        fragment_index += 1

    return fragments_html, json_data

def save_results(fragments: Dict[str, str], data_json: Dict[str, str], page_id: str, lang: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename, content in fragments.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Creato file frammento: {filepath}")
        except Exception as e:
            print(f"ERRORE nella scrittura del file {filepath}: {e}")

    json_filename = f"page_config_{lang}_{page_id}.json"
    json_filepath = os.path.join(OUTPUT_DIR, json_filepath) if 'json_filepath' in locals() else os.path.join(OUTPUT_DIR, json_filename)
    try:
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(data_json, f, indent=4, ensure_ascii=False)
        print(f"\nCreato file JSON di configurazione: {json_filepath}")
        print("Il file JSON mappa le chiavi mainTextX e imageSourceX.")
        print("\nPROCESSO COMPLETATO CON SUCCESSO.")
    except Exception as e:
        print(f"ERRORE nella scrittura del file JSON {json_filepath}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"ERRORE: Argomenti mancanti.")
        print(f"Utilizzo: python {sys.argv[0]} [page_id] [lang] [docx_dir]")
        sys.exit(1)

    PAGE_ID = sys.argv[1].lower()
    LANG = sys.argv[2].lower()
    DOCX_DIR = sys.argv[3]
    
    print(f"Inizio elaborazione per ID Pagina: {PAGE_ID}, Lingua: {LANG}")
    
    raw_html_content = ""
    full_html_path = os.path.join(DOCX_DIR, TEMP_HTML_FILENAME)
    
    try:
        with open(full_html_path, 'r', encoding='utf-8') as f:
            raw_html_content = f.read()
        print(f"File grezzo '{full_html_path}' letto con successo.")
    except FileNotFoundError:
        print(f"ERRORE FATALE: File HTML grezzo '{full_html_path}' non trovato.")
        sys.exit(1)
    except Exception as e:
        print(f"ERRORE durante la lettura del file HTML grezzo: {e}")
        sys.exit(1)
        
    fragments, config_data = process_document(raw_html_content, LANG, PAGE_ID)
    save_results(fragments, config_data, PAGE_ID, LANG)
    
    print(f"Pulizia del file temporaneo {TEMP_HTML_FILENAME} in {DOCX_DIR}...")
    try:
        os.remove(full_html_path)
        print("Pulizia completata.")
    except OSError as e:
        print(f"ATTENZIONE: Impossibile eliminare il file temporaneo {full_html_path}: {e}")