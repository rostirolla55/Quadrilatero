import os
import sys
import shutil

def create_dettaglio_html_pages(page_id):
    # Evita il doppio suffisso se page_id contiene già '_dett_' o '_dettaglio'
    if "_dett_" in page_id or page_id.endswith("_dettaglio"):
        base_name = page_id
    else:
        base_name = f"{page_id}_dettaglio"

    for lang in ["it", "en", "es", "fr"]:
        template_path = f"template_dettaglio-{lang}.html"
        if not os.path.exists(template_path):
            print(f"Errore: Template '{template_path}' non trovato nella root.")
            sys.exit(1)

        target_html = f"{base_name}-{lang}.html"
        shutil.copyfile(template_path, target_html)
        print(f"Creato contenitore dettaglio: {target_html} (da {template_path})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python crea_pagine_dettaglio.py <page_id>")
        sys.exit(1)
    create_dettaglio_html_pages(sys.argv[1])