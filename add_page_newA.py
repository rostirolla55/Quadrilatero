import os
import shutil
import datetime
import re

# Supponiamo che queste costanti siano definite all'inizio del tuo script originale
# HTML_TEMPLATE_NAME = "template.html"
# LANGUAGES = ["it", "en", "es", "fr"]
# HTML_NAV_MARKER = "<!-- [NAV_MARKER] -->"

def update_html_files(repo_root, page_id, nav_key_id, translations, page_title_it):
    """
    1. Crea fisicamente i nuovi file HTML (it, en, es, fr) partendo dal template.
    2. Aggiorna il menu in TUTTI i file HTML, incluso il template stesso.
    """
    template_path = os.path.join(repo_root, HTML_TEMPLATE_NAME)
    today_version = datetime.datetime.now().strftime("%Y%m%d_%H%M")

    if not os.path.exists(template_path):
        print(f"ERRORE: Template {HTML_TEMPLATE_NAME} non trovato in {repo_root}")
        return

    # --- 1. CREAZIONE NUOVI FILE ---
    # Questa parte rimane identica: copia il template PRIMA che venga aggiornato col nuovo link,
    # poi personalizza ID e lingua.
    for lang in LANGUAGES:
        new_filename = f"{page_id}-{lang}.html" if lang != "it" else f"{page_id}.html"
        new_path = os.path.join(repo_root, new_filename)

        if not os.path.exists(new_path):
            shutil.copyfile(template_path, new_path)
            with open(new_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Personalizza ID body e attributo lang
            content = content.replace('id="template"', f'id="{page_id}"')
            content = re.sub(r'<html lang="[a-z]{2}">', f'<html lang="{lang}">', content)

            # Nota: Hai rimosso il marker dello switcher perché sono cablate, 
            # quindi questa parte potrebbe non trovare nulla ma non fa danni.
            if "LANGUAGE_SWITCHER_MARKER" in locals() and LANGUAGE_SWITCHER_MARKER in content:
                switcher = generate_language_switcher(page_id, lang)
                content = content.replace(LANGUAGE_SWITCHER_MARKER, switcher)

            with open(new_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Creata nuova pagina: {new_filename}")

    # --- 2. AGGIORNAMENTO MENU IN TUTTI I FILE (INCLUSO IL TEMPLATE) ---
    
    # MODIFICA: Rimuoviamo il filtro "and f != HTML_TEMPLATE_NAME"
    # Ora all_files includerà anche template.html
    all_files = [
        f for f in os.listdir(repo_root) if f.endswith(".html")
    ]

    for filename in all_files:
        file_path = os.path.join(repo_root, filename)

        # Determiniamo la lingua del file per mettere l'etichetta corretta nel menu
        current_lang = "it"
        for l in ["en", "es", "fr"]:
            if f"-{l}.html" in filename:
                current_lang = l
        
        # Se il file è proprio il template.html, decidiamo quale lingua usare per il link.
        # Spesso conviene usare "it" come default per il template.
        if filename == HTML_TEMPLATE_NAME:
            current_lang = "it"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if f'id="{nav_key_id}"' not in content:
                # Se è italiano va a paginaxy.html, altrimenti paginaxy-en.html ecc.
                target_href = (
                    f"{page_id}-{current_lang}.html"
                    if current_lang != "it"
                    else f"{page_id}.html"
                )
                label = translations.get(current_lang, page_title_it)

                # Prepariamo la riga del menu
                nav_link = f'                <li><a id="{nav_key_id}" href="{target_href}">{label}</a></li>'

                # Inserimento nel punto marcato
                if HTML_NAV_MARKER in content:
                    parts = content.rsplit(HTML_NAV_MARKER, 1)
                    content = (
                        parts[0] + nav_link + "\n            " + HTML_NAV_MARKER + parts[1]
                    )

                # Cache busting (aggiorna la versione del JS per evitare vecchie cache)
                content = re.sub(
                    r"main\.js\?v=[0-9A-Z_]*", f"main.js?v={today_version}", content
                )

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Menu aggiornato in {filename}")

        except Exception as e:
            print(f"Errore durante l'aggiornamento di {filename}: {e}")