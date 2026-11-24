# -*- coding: utf-8 -*-
import os
import re
import shutil
import subprocess
import sys

LANGUAGES = ["it", "en", "es", "fr"]


# =====================================================================
# BLOCCO 1: Validazione convenzione [poi]_dett_[nome] e percorsi base
# =====================================================================
def valida_id_dettaglio(dettaglio_id: str) -> str:
    dettaglio_id = (dettaglio_id or "").strip()
    if not dettaglio_id:
        raise ValueError("ID dettaglio vuoto.")

    if not re.match(r"^[a-z0-9]+(?:_[a-z0-9]+)*_dett_[a-z0-9]+(?:_[a-z0-9]+)*$", dettaglio_id):
        print(
            f"[AVVISO] '{dettaglio_id}' non segue esattamente lo standard '[poi]_dett_[nome]' "
            "(minuscole, numeri e underscore)."
        )
    return dettaglio_id


# =====================================================================
# BLOCCO 2: Creazione pagine HTML di dettaglio ([poi]_dett_[nome]-[lang].html)
# =====================================================================
def crea_html_dettaglio(dettaglio_id: str, repo_root: str) -> list:
    creati = []
    fallback_template = os.path.join(repo_root, "template_dettaglio-it.html")

    print("--- Blocco 2: Generazione HTML di dettaglio ---")
    for lang in LANGUAGES:
        template_path = os.path.join(repo_root, f"template_dettaglio-{lang}.html")
        target_path = os.path.join(repo_root, f"{dettaglio_id}-{lang}.html")

        if os.path.exists(template_path):
            shutil.copyfile(template_path, target_path)
            print(f"  [OK] {os.path.basename(target_path)} <- {os.path.basename(template_path)}")
            creati.append(target_path)
        elif os.path.exists(fallback_template):
            shutil.copyfile(fallback_template, target_path)
            print(f"  [FALLBACK] {os.path.basename(target_path)} <- template_dettaglio-it.html")
            creati.append(target_path)
        else:
            print(f"  [ERRORE] Template mancante per lingua '{lang}' e fallback assente.")

    return creati


# =====================================================================
# BLOCCO 3: Cartelle di supporto per dettaglio (no pois_config.json / no main.js)
# =====================================================================
def prepara_cartelle_dettaglio(dettaglio_id: str, repo_root: str) -> None:
    print("--- Blocco 3: Verifica cartelle immagini e text_files ---")
    dirs_da_garantire = [
        os.path.join(repo_root, "text_files"),
        os.path.join(repo_root, "Assets", "images", dettaglio_id, "dettaglio"),
    ]
    for d in dirs_da_garantire:
        os.makedirs(d, exist_ok=True)
        print(f"  [OK] Cartella pronta: {d}")


# =====================================================================
# BLOCCO 4: Tracciamento e coordinamento flusso locale
# =====================================================================
def traccia_operazione(dettaglio_id: str, repo_root: str) -> None:
    nota_bat = os.path.join(repo_root, "Utilities", "nota.bat")
    if os.path.exists(nota_bat):
        subprocess.run([nota_bat, "create_newdettaglio", dettaglio_id], check=False)


def main() -> int:
    repo_root = os.path.dirname(os.path.abspath(__file__))
    dettaglio_id = sys.argv[1] if len(sys.argv) > 1 else input("ID dettaglio ([poi]_dett_[nome]): ")

    try:
        dettaglio_id = valida_id_dettaglio(dettaglio_id)
    except ValueError as exc:
        print(f"[ERRORE] {exc}")
        return 1

    crea_html_dettaglio(dettaglio_id, repo_root)
    prepara_cartelle_dettaglio(dettaglio_id, repo_root)
    traccia_operazione(dettaglio_id, repo_root)

    print(f"\nCompletato per '{dettaglio_id}' senza modificare pois_config.json o main.js.")
    return 0


if __name__ == "__main__":
    sys.exit(main())