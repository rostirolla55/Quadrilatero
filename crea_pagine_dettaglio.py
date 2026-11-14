import os
import sys
import shutil

def create_dettaglio_html_pages(page_id, template_path="dettaglio_template.html"):
    if not os.path.exists(template_path):
        print(f"Errore: Template '{template_path}' non trovato nella root.")
        sys.exit(1)

    for lang in ["it", "en", "es", "fr"]:
        target_html = f"{page_id}_dettaglio-{lang}.html"
        shutil.copyfile(template_path, target_html)
        print(f"Creato contenitore dettaglio: {target_html}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python crea_pagine_dettaglio.py <page_id> [template_path]")
        sys.exit(1)
    tpl = sys.argv[2] if len(sys.argv) > 2 else "dettaglio_template.html"
    create_dettaglio_html_pages(sys.argv[1], tpl)