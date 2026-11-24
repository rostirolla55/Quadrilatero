# -*- coding: utf-8 -*-
import sys
import os
import re
import json


def pulisci_e_splitta_html(lang, poi_id, is_dettaglio=False):
    """
    Legge l'HTML temporaneo generato da LibreOffice, lo pulisce dai tag inutili,
    aggiorna i percorsi delle immagini e lo suddivide in file distinti in base al tipo (mainText o dettText).
    """
    if is_dettaglio:
        cand_dett = f"temp_{lang}_{poi_id}_dett.html"
        cand_dettagli = f"temp_{lang}_{poi_id}_dettagli.html"
        html_input = cand_dett if os.path.exists(cand_dett) else cand_dettagli
    else:
        html_input = f"temp_{lang}_{poi_id}.html"
        
    if not os.path.exists(html_input):
        print(f" [ERRORE] File temporaneo non trovato: {html_input}")
        return

    with open(html_input, 'r', encoding='utf-8') as f:
        contenuto = f.read()

    # --- 1. PULIZIA HTML SPURIO DA LIBREOFFICE ---
    contenuto = re.sub(r'<!--.*?-->', '', contenuto, flags=re.DOTALL)
    contenuto = re.sub(r'<style.*?>.*?</style>', '', contenuto, flags=re.DOTALL | re.IGNORECASE)
    contenuto = re.sub(r'</?(?:html|head|body|meta)[^>]*>', '', contenuto, flags=re.IGNORECASE)

    # --- 1.5 ESTRAZIONE ORDINE IMMAGINI DAI TAG [SPLIT_BLOCK:nome_file.ext] ---
    split_images = re.findall(r'\[SPLIT_BLOCK:([^\]]+)\]', contenuto, flags=re.IGNORECASE)
    split_images = [os.path.basename(img.strip()) for img in split_images if img.strip()]

    # --- 1.6 CORREZIONE PERCORSI IMMAGINI INLINE NEL DETTAGLIO ---
    if is_dettaglio:
        def fix_img_src(match):
            img_tag = match.group(0)
            src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag, re.IGNORECASE)
            if src_match:
                original_src = src_match.group(1)
                filename = os.path.basename(original_src)
                new_src = f"Assets/images/{poi_id}/dettaglio/{filename}"
                return re.sub(r'src=["\']([^"\']+)["\']', f'src="{new_src}"', img_tag, flags=re.IGNORECASE)
            return img_tag

        contenuto = re.sub(r'<img[^>]+>', fix_img_src, contenuto, flags=re.IGNORECASE)

    # --- 2. SDOPPIAMENTO BLOCCHI TRAMITE [SPLIT_BLOCK] ---
    pattern_split = r'(?:<p[^>]*>)?\s*(?:<span[^>]*>)?\s*\[SPLIT_BLOCK(?::[^\]]+)?\]\s*(?:</span>)?\s*(?:</p>)?'
    blocchi_raw = re.split(pattern_split, contenuto, flags=re.IGNORECASE)

    blocchi_puliti = []
    for b in blocchi_raw:
        b_clean = b.strip()
        if b_clean:
            blocchi_puliti.append(b_clean)

    out_dir = "text_files"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # --- 3. GENERAZIONE DEI FILE HTML DEDICATI ---
    if is_dettaglio:
        prefix_key = "dettText"
        print(f" [DETTAGLIO] Generazione file {prefix_key}1..5 per {lang}_{poi_id}...")
    else:
        prefix_key = "maintext"
        print(f" [PRINCIPALE] Generazione file {prefix_key}1..5 per {lang}_{poi_id}...")

    for idx in range(1, 6):
        nome_file = f"{lang}_{poi_id}_{prefix_key}{idx}.html"
        percorso_file = os.path.join(out_dir, nome_file)

        if idx <= len(blocchi_puliti):
            testo_blocco = blocchi_puliti[idx - 1]
            with open(percorso_file, 'w', encoding='utf-8') as f_out:
                f_out.write(testo_blocco)
            print(f" ✓ Creato: {nome_file}")
        else:
            if os.path.exists(percorso_file):
                with open(percorso_file, 'w', encoding='utf-8') as f_out:
                    f_out.write("")
                print(f" - Svuotato (inutilizzato): {nome_file}")

    # --- 4. GENERAZIONE FILE DI CONFIGURAZIONE PER sync_config.py ---
    config_data = {}
    for idx in range(1, 6):
        nome_file = f"{lang}_{poi_id}_{prefix_key}{idx}.html"
        percorso_file = os.path.join(out_dir, nome_file)
        chiave_json = f"dettText{idx}" if is_dettaglio else f"mainText{idx}"
        if os.path.exists(percorso_file) and os.path.getsize(percorso_file) > 0:
            config_data[chiave_json] = f"{out_dir}/{nome_file}"
        else:
            config_data[chiave_json] = ""

    # Associa le immagini seguendo l'ordine dichiarato nei tag [SPLIT_BLOCK:...]
    # (con fallback sull'ordine alfabetico della cartella se i tag non hanno il nome file)
    img_dir = os.path.join("Assets", "images", poi_id)
    img_prefix = "imageDett" if is_dettaglio else "imageSource"
    rel_img_prefix = f"{poi_id}/dettaglio" if is_dettaglio else f"{poi_id}"
    if is_dettaglio:
        img_dir = os.path.join(img_dir, "dettaglio")

    immagini = []
    if split_images:
        immagini = split_images
    elif os.path.exists(img_dir):
        immagini = sorted([
            f for f in os.listdir(img_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
            and os.path.isfile(os.path.join(img_dir, f))
        ])

    for idx in range(1, 6):
        if idx <= len(immagini) and immagini[idx - 1]:
            config_data[f"{img_prefix}{idx}"] = f"{rel_img_prefix}/{immagini[idx - 1]}"
        else:
            config_data[f"{img_prefix}{idx}"] = ""

    suffix_cfg = "_dettagli" if is_dettaglio else ""
    config_filename = f"page_config_{lang}_{poi_id}{suffix_cfg}.json"
    config_path = os.path.join(out_dir, config_filename)
    with open(config_path, 'w', encoding='utf-8') as f_cfg:
        json.dump(config_data, f_cfg, indent=4, ensure_ascii=False)
    print(f" ✓ Generato file config: {config_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python post_process_html.py <lang> <poi_id> [--dettagli]")
        sys.exit(1)

    lingua = sys.argv[1]
    pagina_id = sys.argv[2]
    flag_dettaglio = "--dettagli" in sys.argv or (len(sys.argv) > 3 and sys.argv[3] == "dettagli")

    pulisci_e_splitta_html(lingua, pagina_id, is_dettaglio=flag_dettaglio)
