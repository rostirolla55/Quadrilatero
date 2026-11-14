import os
import sys


def main():
    if len(sys.argv) < 2:
        print("Errore: Specificare il nome della pagina (es. arco125_francesi)")
        print("Uso: python trasfer_in_qrtp.py <nome_pagina> [--dettaglio]")
        sys.exit(1)

    raw_args = [arg.strip().lower() for arg in sys.argv[1:]]
    is_dettaglio = "--dettaglio" in raw_args or "-d" in raw_args

    clean_args = [arg for arg in raw_args if not arg.startswith("-")]
    if not clean_args:
        print("Errore: Nome della pagina non specificato.")
        sys.exit(1)

    page_name = clean_args[0]
    langs = ["it", "en", "es", "fr"]

    src_base = r"C:\Users\User\Documents\GitHub\Quadrilatero"
    dst_base = r"C:\Users\User\Documents\GitHub\QuartierePorto"

    suffix = "_dettaglio" if is_dettaglio else ""
    bat_filename = f"trasfer_{page_name}{suffix}_in_qrtp.bat"

    copy_tasks = []

    # --------------------------------------------------------------------------
    # 1. FILE HTML NELLA ROOT (Standard unificato + retrocompatibilità)
    # --------------------------------------------------------------------------
    html_patterns = []

    dettaglio_patterns = [f"{page_name}_dettaglio.html"]
    for lang in langs:
        dettaglio_patterns.extend([
            f"{page_name}_dettaglio-{lang}.html",   # Standard unificato
            f"{lang}_{page_name}_dettagli.html",    # Formato precedente
            f"dettaglio_{page_name}-{lang}.html",   # Formato legacy
        ])

    if is_dettaglio:
        html_patterns.extend(dettaglio_patterns)
    else:
        html_patterns.append(f"{page_name}.html")
        for lang in langs:
            html_patterns.append(f"{page_name}-{lang}.html")
        html_patterns.extend(dettaglio_patterns)

    for h in html_patterns:
        src_path = os.path.join(src_base, h)
        if os.path.exists(src_path):
            copy_tasks.append((src_path, os.path.join(dst_base, h)))

    # --------------------------------------------------------------------------
    # 1b. FRAMMENTI HTML NELLA ROOT (se caricati dalla root dal browser)
    # --------------------------------------------------------------------------
    for f in os.listdir(src_base):
        f_low = f.lower()
        if f_low.endswith(".html") and page_name in f_low and (
            "maintext" in f_low or "detttext" in f_low
        ):
            copy_tasks.append((os.path.join(src_base, f), os.path.join(dst_base, f)))

    # --------------------------------------------------------------------------
    # 2. FILE TESTUALI E DI CONFIGURAZIONE (in text_files\)
    # --------------------------------------------------------------------------
    text_dir_src = os.path.join(src_base, "text_files")
    text_dir_dst = os.path.join(dst_base, "text_files")
    if os.path.exists(text_dir_src):
        for f in os.listdir(text_dir_src):
            if page_name in f.lower():
                copy_tasks.append(
                    (os.path.join(text_dir_src, f), os.path.join(text_dir_dst, f))
                )

    # --------------------------------------------------------------------------
    # 3. IMMAGINI (Assets\images\[pagina] e Assets\images\[pagina]\dettaglio)
    # --------------------------------------------------------------------------
    img_folders = [
        os.path.join("Assets", "images", page_name),
        os.path.join("Assets", "images", page_name, "dettaglio"),
        os.path.join("Assets", "images", f"dettaglio_{page_name}"),
    ]
    for rel_folder in img_folders:
        img_dir_src = os.path.join(src_base, rel_folder)
        img_dir_dst = os.path.join(dst_base, rel_folder)
        if os.path.exists(img_dir_src):
            for f in os.listdir(img_dir_src):
                src_file = os.path.join(img_dir_src, f)
                if os.path.isfile(src_file):
                    copy_tasks.append((src_file, os.path.join(img_dir_dst, f)))

    # --------------------------------------------------------------------------
    # 4. FILE AUDIO MP3 (Assets\Audio\[lang]\[pagina].mp3 e _dettaglio.mp3)
    # --------------------------------------------------------------------------
    audio_candidates = [
        f"{page_name}.mp3",
        f"{page_name}_dettaglio.mp3",
        f"dettaglio_{page_name}.mp3",
    ]

    for lang in langs:
        audio_src_dir = os.path.join(src_base, "Assets", "Audio", lang)
        audio_dst_dir = os.path.join(dst_base, "Assets", "Audio", lang)
        for audio_file in audio_candidates:
            src_audio = os.path.join(audio_src_dir, audio_file)
            if os.path.exists(src_audio):
                copy_tasks.append((src_audio, os.path.join(audio_dst_dir, audio_file)))

    # --------------------------------------------------------------------------
    # 5. GENERAZIONE DEL FILE BATCH CON ROBOCOPY
    # --------------------------------------------------------------------------
    bat_content = [
        "@echo off",
        ":: File batch generato automaticamente per il trasferimento su QuartierePorto",
        f":: Pagina: {page_name} (Modalita: {'Dettaglio' if is_dettaglio else 'Generale/Auto'})",
        "chcp 65001 >nul",
        "echo Avvio trasferimento con preservazione dei timestamp...",
        "",
    ]

    for src, dst in copy_tasks:
        src_dir = os.path.dirname(src)
        dst_dir = os.path.dirname(dst)
        filename = os.path.basename(src)
        robocopy_cmd = (
            f'robocopy "{src_dir}" "{dst_dir}" "{filename}" /COPY:DAT /DCOPY:DAT /R:2 /W:2'
        )
        bat_content.append(robocopy_cmd)

    bat_content.extend(["", "echo.", "echo Trasferimento completato!", "pause"])

    output_bat_path = os.path.join(src_base, bat_filename)
    with open(output_bat_path, "w", encoding="utf-8") as f:
        f.write("\n".join(bat_content))

    print(f"Generato con successo: {bat_filename}")
    print(f"Totale file gestiti da trasferire: {len(copy_tasks)}")


if __name__ == "__main__":
    main()