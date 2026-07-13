import os
import sys
import shutil
from datetime import datetime

def elabora_pagina_turismo(nome_pagina, lingue=['it', 'en', 'fr', 'es']):
    # Uniforma il parametro (es. 'carracci' o 'Carracci')
    nome_pagina = nome_pagina.strip().lower().replace(".docx", "")
    
    # --- CONTROLLO BLOCCANTE: Verifica l'esistenza di tutti gli 8 file richiesti ---
    file_richiesti = []
    for lingua in lingue:
        file_richiesti.append(f"{nome_pagina}_{lingua}.docx")
        file_richiesti.append(f"{nome_pagina}_analysis_{lingua}.docx")
        
    file_mancanti = [f for f in file_richiesti if not os.path.exists(f)]
    
    if file_mancanti:
        print(f"❌ BLOCCO DI SICUREZZA: Impossibile procedere per '{nome_pagina}'.")
        print("   Mancano i seguenti file necessari nella cartella:")
        for fm in sorted(file_mancanti):
            print(f"   - {fm}")
        print("\nVerifica di aver generato tutte le lingue e riprova.")
        return False

    print(f"=== INIZIO PROCESSO DI SICUREZZA PER: {nome_pagina.upper()} ===")
    print("✅ Tutti gli 8 file (Standard + Analysis) sono presenti. Eseguo i passaggi.\n")

    # --- CICLO DI ELABORAZIONE IMMEDIATA PER OGNI LINGUA ---
    for lingua in lingue:
        file_standard = f"{nome_pagina}_{lingua}.docx"
        file_analysis = f"{nome_pagina}_analysis_{lingua}.docx"
        
        # Genera il timestamp preciso nel formato richiesto (es. 20260628_18034544)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:15]
        file_backup = f"{nome_pagina}_{lingua}@{timestamp}.docx"
        
        print(f"➔ Lingua: {lingua.upper()}")
        
        # --- PASSO 1: Crea la copia di backup dal file standard esistente ---
        try:
            shutil.copy2(file_standard, file_backup)
            print(f"    1) Backup creato: '{file_standard}' ➡️ '{file_backup}'")
        except Exception as e:
            print(f"    ❌ Errore critico al Passo 1 (Copia di backup): {e}")
            return False
        
        # --- PASSO 2: Verifica l'integrità tra il file standard e il backup ---
        if os.path.exists(file_backup):
            dim_standard = os.path.getsize(file_standard)
            dim_backup = os.path.getsize(file_backup)
            
            if dim_standard == dim_backup:
                print(f"    2) Verifica Integrità superata: '{file_backup}' e '{file_standard}' coincidono ({dim_backup} byte).")
            else:
                print(f"    ❌ Errore critico al Passo 2: Dimensione del backup non corrispondente! Interrompo.")
                return False
        else:
            print(f"    ❌ Errore critico al Passo 2: Il file di backup non è presente su disco.")
            return False

        # --- PASSO 3: Rinomina/Copia il file generato in formato standard pulito ---
        try:
            shutil.copy2(file_analysis, file_standard)
            print(f"    3) Aggiornamento completato: '{file_analysis}' ➡️ '{file_standard}'")
        except Exception as e:
            print(f"    ❌ Errore critico al Passo 3 (Sovrascrittura standard): {e}")
            return False
            
        print("-" * 50)

    print(f"=== ELABORAZIONE COMPLETATA CON SUCCESSO PER: {nome_pagina.upper()} ===\n")
    return True

# --- ESECUZIONE DIRETTA TRAMITE PARAMETRO ESTERNO ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        nome_da_procedura = sys.argv[1]
        elabora_pagina_turismo(nome_da_procedura)
    else:
        print("❌ Errore: Manca il nome della pagina come parametro della riga di comando.")
        print("Uso corretto: python nome_script.py nome_pagina")
        print("Esempio: python nome_script.py carracci")