import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Errore: Specificare il nome della pagina (es. pittoricarracci)")
        sys.exit(1)

    page_name = sys.argv[1].lower().strip()
    
    # Percorsi base
    src_base = r"C:\Users\User\Documents\GitHub\Quadrilatero"
    dst_base = r"C:\Users\User\Documents\GitHub\QuartierePorto"
    
    bat_filename = f"trasfer_{page_name}_in_qrtp.bat"
    
    # Lista delle operazioni di copia (file_sorgente, file_destinazione)
    copy_tasks = []

    # 1. File HTML principali
    html_files = [
        f"{page_name}.html",
        f"{page_name}-it.html",
        f"{page_name}-en.html",
        f"{page_name}-es.html",
        f"{page_name}-fr.html"
    ]
    for h in html_files:
        src_path = os.path.join(src_base, h)
        if os.path.exists(src_path):
            copy_tasks.append((src_path, os.path.join(dst_base, h)))

    # 2. File di configurazione e testi in text_files
    text_dir_src = os.path.join(src_base, "text_files")
    text_dir_dst = os.path.join(dst_base, "text_files")
    if os.path.exists(text_dir_src):
        for f in os.listdir(text_dir_src):
            if page_name in f.lower():
                copy_tasks.append((os.path.join(text_dir_src, f), os.path.join(text_dir_dst, f)))

    # 3. Immagini in Assets/images/[pagina]
    img_dir_src = os.path.join(src_base, "Assets", "images", page_name)
    img_dir_dst = os.path.join(dst_base, "Assets", "images", page_name)
    if os.path.exists(img_dir_src):
        for f in os.listdir(img_dir_src):
            copy_tasks.append((os.path.join(img_dir_src, f), os.path.join(img_dir_dst, f)))

    # 4. Audio nelle varie lingue Assets/Audio/[lang]/[pagina].mp3
    langs = ["it", "en", "es", "fr"]
    for lang in langs:
        audio_src_dir = os.path.join(src_base, "Assets", "Audio", lang)
        audio_dst_dir = os.path.join(dst_base, "Assets", "Audio", lang)
        audio_file = f"{page_name}.mp3"
        src_audio = os.path.join(audio_src_dir, audio_file)
        if os.path.exists(src_audio):
            copy_tasks.append((src_audio, os.path.join(audio_dst_dir, audio_file)))

    # Generazione del file .bat
    bat_content = [
        "@echo off",
        ":: File batch generato automaticamente per il trasferimento su QuartierePorto",
        f":: Pagina: {page_name}",
        "chcp 65001 >nul",
        "echo Avvio trasferimento con preservazione dei timestamp...",
        ""
    ]

    for src, dst in copy_tasks:
        src_dir = os.path.dirname(src)
        dst_dir = os.path.dirname(dst)
        filename = os.path.basename(src)
        
        # Usiamo robocopy per preservare esattamente le date di creazione/modifica (/COPY:DAT /DCOPY:DAT)
        # Sintassi robocopy: robocopy "sorgente_dir" "destinazione_dir" "file" [opzioni]
        robocopy_cmd = f'robocopy "{src_dir}" "{dst_dir}" "{filename}" /COPY:DAT /DCOPY:DAT /R:2 /W:2'
        bat_content.append(robocopy_cmd)

    bat_content.extend([
        "",
        "echo.",
        "echo Trasferimento completato!",
        "pause"
    ])

    # Scrittura del file batch risultante
    output_bat_path = os.path.join(src_base, bat_filename)
    with open(output_bat_path, "w", encoding="utf-8") as f:
        f.write("\n".join(bat_content))

    print(f"Generato con successo: {bat_filename}")
    print(f"Totale file gestiti: {len(copy_tasks)}")

if __name__ == "__main__":
    main()