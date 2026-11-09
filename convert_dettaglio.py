import os
import sys
import subprocess

def main():
    # Controllo argomenti in ingresso da convert_dettaglio.bat
    # Sintassi attesa: python convert_dettaglio.py <lingua> <nome_pagina> [--dettaglio]
    if len(sys.argv) < 3:
        print("[ERRORE] Argomenti insufficienti per convert_dettaglio.py")
        print("Uso: python convert_dettaglio.py <lingua> <nome_pagina> [--dettaglio]")
        sys.exit(1)

    lingua = sys.argv[1].lower().strip()
    page_name = sys.argv[2].lower().strip()
    
    # Verifica se e stato passato il flag --dettaglio (facoltativo)
    is_dettaglio = "--dettaglio" in [arg.lower() for arg in sys.argv] or True  # Di default gestisce il dettaglio

    print(f"=== Avvio Elaborazione Dettaglio ===")
    print(f"Lingua: {lingua}")
    print(f"Pagina: {page_name}")
    print(f"Modalita Dettaglio: {'Si' if is_dettaglio else 'No'}")

    # Percorsi dei repository
    base_dir = r"C:\Users\User\Documents\GitHub\Quadrilatero"
    trasfer_script = os.path.join(base_dir, "trasfer_in_qrtp.py")

    # 1. Verifiche preliminari sui file del dettaglio
    filename_html = f"dettaglio_{page_name}-{lingua}.html"
    file_html_path = os.path.join(base_dir, filename_html)

    if os.path.exists(file_html_path):
        print(f"[OK] Trovato file HTML di dettaglio: {filename_html}")
    else:
        print(f"[AVVISO] File HTML '{filename_html}' non ancora presente in {base_dir}")

    # 2. Invocazione di trasfer_in_qrtp.py per generare il batch di copia verso QuartierePorto
    if os.path.exists(trasfer_script):
        cmd = [sys.executable, trasfer_script, page_name, "--dettaglio"]
        print(f"\n[INFO] Esecuzione trasfer_in_qrtp.py...")
        result = subprocess.run(cmd, capture_output=False)
        
        if result.returncode == 0:
            print(f"[OK] File batch di trasferimento per '{page_name}' generato con successo.")
        else:
            print(f"[ERRORE] Errore durante l'esecuzione di trasfer_in_qrtp.py (Codice: {result.returncode})")
            sys.exit(result.returncode)
    else:
        print(f"[ERRORE] Impossibile trovare lo script di trasferimento: {trasfer_script}")
        sys.exit(1)

if __name__ == "__main__":
    main()