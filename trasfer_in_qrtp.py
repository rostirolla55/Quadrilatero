import os  
import sys  
  
def main():  
    # Controllo argomenti in ingresso
    if len(sys.argv) < 2:  
        print("Errore: Specificare il nome della pagina (es. pittoricarracci)")  
        print("Uso: python trasfer_in_qrtp.py <nome_pagina> [--dettaglio]")
        sys.exit(1)  
  
    # Estrazione parametri
    raw_args = [arg.strip().lower() for arg in sys.argv[1:]]
    
    # Verifica presenza del flag --dettaglio o -d
    is_dettaglio = "--dettaglio" in raw_args or "-d" in raw_args
    
    # Pulizia del nome pagina escludendo eventuali flag
    clean_args = [arg for arg in raw_args if not arg.startswith("-")]
    if not clean_args:
        print("Errore: Nome della pagina non specificato.")
        sys.exit(1)
        
    page_name = clean_args[0]
   
    # Percorsi base dei repository
    src_base = r"C:\Users\User\Documents\GitHub\Quadrilatero"  
    dst_base = r"C:\Users\User\Documents\GitHub\QuartierePorto"  
   
    # Nome del file batch di output generato
    suffix = "_dettaglio" if is_dettaglio else ""
    bat_filename = f"trasfer_{page_name}{suffix}_in_qrtp.bat"  
   
    # Lista delle operazioni di copia: tuple (file_sorgente, file_destinazione)  
    copy_tasks = []  
  
    # --------------------------------------------------------------------------
    # 1. FILE HTML (Principali e Dettagli)
    # --------------------------------------------------------------------------
    # Genera sia i pattern standard (es. carracci-it.html) che dettaglio (es. dettaglio_carracci-it.html)
    html_patterns = []
    
    # Se specificato il flag o se si tratta di una pagina di dettaglio
    if is_dettaglio:
        html_patterns.extend([
            f"dettaglio_{page_name}.html",
            f"dettaglio_{page_name}-it.html",
            f"dettaglio_{page_name}-en.html",
            f"dettaglio_{page_name}-es.html",
            f"dettaglio_{page_name}-fr.html"
        ])
    else:
        # Inclusione completa di entrambi i formati per ricerca automatica
        html_patterns.extend([
            f"{page_name}.html",
            f"{page_name}-it.html",
            f"{page_name}-en.html",
            f"{page_name}-es.html",
            f"{page_name}-fr.html",
            f"dettaglio_{page_name}.html",
            f"dettaglio_{page_name}-it.html",
            f"dettaglio_{page_name}-en.html",
            f"dettaglio_{page_name}-es.html",
            f"dettaglio_{page_name}-fr.html"
        ])

    for h in html_patterns:  
        src_path = os.path.join(src_base, h)  
        if os.path.exists(src_path):  
            copy_tasks.append((src_path, os.path.join(dst_base, h)))  
  
    # --------------------------------------------------------------------------
    # 2. FILE TESTUALI E DI CONFIGURAZIONE (in text_files\)
    # --------------------------------------------------------------------------
    text_dir_src = os.path.join(src_base, "text_files")  
    text_dir_dst = os.path.join(dst_base, "text_files")  
    if os.path.exists(text_dir_src):  
        for f in os.listdir(text_dir_src):  
            # Copia file che contengono il nome pagina o l'eventuale prefisso dettaglio
            if page_name in f.lower():  
                copy_tasks.append((os.path.join(text_dir_src, f), os.path.join(text_dir_dst, f)))  
  
    # --------------------------------------------------------------------------
    # 3. IMMAGINI (Assets\images\[pagina] o Assets\images\dettaglio_[pagina])
    # --------------------------------------------------------------------------
    img_folders = [page_name, f"dettaglio_{page_name}"]
    for folder in img_folders:
        img_dir_src = os.path.join(src_base, "Assets", "images", folder)  
        img_dir_dst = os.path.join(dst_base, "Assets", "images", folder)  
        if os.path.exists(img_dir_src):  
            for f in os.listdir(img_dir_src):  
                copy_tasks.append((os.path.join(img_dir_src, f), os.path.join(img_dir_dst, f)))  
  
    # --------------------------------------------------------------------------
    # 4. FILE AUDIO MP3 (Assets\Audio\[lang]\[pagina].mp3 e dettaglio_[pagina].mp3)
    # --------------------------------------------------------------------------
    langs = ["it", "en", "es", "fr"]  
    audio_candidates = [f"{page_name}.mp3", f"dettaglio_{page_name}.mp3"]
    
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
        ""  
    ]  
  
    for src, dst in copy_tasks:  
        src_dir = os.path.dirname(src)  
        dst_dir = os.path.dirname(dst)  
        filename = os.path.basename(src)  
        
        # Robocopy preserva date di creazione/modifica (/COPY:DAT /DCOPY:DAT)
        robocopy_cmd = f'robocopy "{src_dir}" "{dst_dir}" "{filename}" /COPY:DAT /DCOPY:DAT /R:2 /W:2'  
        bat_content.append(robocopy_cmd)  
  
    bat_content.extend([  
        "",  
        "echo.",  
        "echo Trasferimento completato!",  
        "pause"  
    ])  
  
    # Scrittura su disco del file batch risultante
    output_bat_path = os.path.join(src_base, bat_filename)  
    with open(output_bat_path, "w", encoding="utf-8") as f:  
        f.write("\n".join(bat_content))  
  
    print(f"Generato con successo: {bat_filename}")  
    print(f"Totale file gestiti da trasferire: {len(copy_tasks)}")  

if __name__ == "__main__":  
    main()