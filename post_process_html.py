# -*- coding: utf-8 -*-
import sys
import os
import re

def pulisci_e_splitta_html(lang, poi_id, is_dettaglio=False):
    """
    Legge l'HTML temporaneo generato da LibreOffice, lo pulisce dai tag inutili
    e lo suddivide in file distinti in base al tipo (mainText o dettText).
    """
    # Determinazione nome file temporaneo sorgente
    if is_dettaglio:
        html_input = f"temp_{lang}_{poi_id}_dettagli.html"
    else:
        html_input = f"temp_{lang}_{poi_id}.html"

    if not os.path.exists(html_input):
        print(f"  [ERRORE] File temporaneo non trovato: {html_input}")
        return

    with open(html_input, 'r', encoding='utf-8') as f:
        contenuto = f.read()

    # --- 1. PULIZIA HTML SPURIO DA LIBREOFFICE ---
    # Rimuove commenti, tag head/style e wrapper inutili
    contenuto = re.sub(r'<!--.*?-->', '', contenuto, flags=re.DOTALL)
    contenuto = re.sub(r'<style.*?>.*?</style>', '', contenuto, flags=re.DOTALL)
    
    # --- 2. SDOPPIAMENTO BLOCCI TRAMITE [SPLIT_BLOCK] ---
    # Divide il testo in corrispondenza del marcatore [SPLIT_BLOCK]
    blocchi_raw = contenuto.split("[SPLIT_BLOCK]")
    blocchi_puliti = [b.strip() for b in blocchi_raw if b.strip()]

    # Cartella di destinazione per i file di testo (.html)
    out_dir = "text_files"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # --- 3. GENERAZIONE DEI FILE HTML DEDICATI ---
    if is_dettaglio:
        prefix_key = "dettText"
        print(f"  [DETTAGLIO] Generazione file {prefix_key}1..5 per {lang}_{poi_id}...")
    else:
        prefix_key = "maintext"
        print(f"  [PRINCIPALE] Generazione file {prefix_key}1..5 per {lang}_{poi_id}...")

    # Genera fino a un massimo di 5 blocchi
    for idx in range(1, 6):
        nome_file = f"{lang}_{poi_id}_{prefix_key}{idx}.html"
        percorso_file = os.path.join(out_dir, nome_file)

        if idx <= len(blocchi_puliti):
            testo_blocco = blocchi_puliti[idx - 1]
            with open(percorso_file, 'w', encoding='utf-8') as f_out:
                f_out.write(testo_blocco)
            print(f"    ✓ Creato: {nome_file}")
        else:
            # Se la nuova conversione ha meno blocchi di prima, puliamo l'eventuale file in eccesso
            if os.path.exists(percorso_file):
                with open(percorso_file, 'w', encoding='utf-8') as f_out:
                    f_out.write("")
                print(f"    - Svuotato (inutilizzato): {nome_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python post_process_html.py <lang> <poi_id> [--dettagli]")
        sys.exit(1)

    lingua = sys.argv[1]
    pagina_id = sys.argv[2]
    flag_dettaglio = "--dettagli" in sys.argv or (len(sys.argv) > 3 and sys.argv[3] == "dettagli")

    pulisci_e_splitta_html(lingua, pagina_id, is_dettaglio=flag_dettaglio)