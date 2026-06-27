import os
import shutil
from datetime import datetime

def elabora_pagina_turismo(nome_pagina, lingue=['it', 'en', 'fr', 'es']):
    # Pulisce il parametro passato da spazi o estensioni inserite per errore
    nome_pagina = nome_pagina.strip().lower().replace(".docx", "")
    
    print(f"=== INIZIO PROCESSO DI SICUREZZA PER: {nome_pagina.upper()} ===")
    
    # --- CONTROLLO PREVENTIVO: Verifica la presenza di TUTTI i file analysis ---
    file_mancanti = []
    for lingua in lingue:
        file_analysis = f"{nome_pagina}_analysis_{lingua}.docx"
        if not os.path.exists(file_analysis):
            file_mancanti.append(file_analysis)
            
    if file_mancanti:
        print(f"❌ BLOCCO DI SICUREZZA: Impossibile procedere.")
        print(f"   Mancano i seguenti file generati dall'AI:")
        for fm in file_mancanti:
            print(f"   - {fm}")
        print("\nElaborazione annullata. Carica i file mancanti per sbloccare la procedura.")
        return False

    print("✅ Verifica iniziale superata: tutti i file '_analysis_' sono presenti. Eseguo subito i passaggi.\n")

    # --- CICLO DI ELABORAZIONE IMMEDIATA PER OGNI LINGUA ---
    for lingua in lingue:
        file_standard = f"{nome_pagina}_{lingua}.docx"
        file_analysis = f"{nome_pagina}_analysis_{lingua}.docx"
        
        # Genera il timestamp preciso nel formato richiesto (es. 20260627_17264044)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:15]
        file_backup = f"{nome_pagina}_{lingua}@{timestamp}.docx"
        
        print(f"➔ Lingua: {lingua.upper()}")
        
        # --- PASSO 1: Crea la copia di backup dal file standard esistente ---
        if not os.path.exists(file_standard):
            print(f"    [Info] Nessun file standard precedente trovato ('{file_standard}'). Salto i passi 1 e 2.")
            backup_eseguito = False
        else:
            try:
                shutil.copy2(file_standard, file_backup)
                print(f"    1) Backup creato: '{file_standard}' ➡️ '{file_backup}'")
                backup_eseguito = True
            except Exception as e:
                print(f"    ❌ Errore critico al Passo 1 (Copia di backup): {e}")
                return False
        
        # --- PASSO 2: Verifica l'integrità tra il file standard e il backup ---
        if backup_eseguito:
            if os.path.exists(file_backup):
                dim_standard = os.path.getsize(file_standard)
                dim_backup = os.path.getsize(file_backup)
                
                if dim_standard == dim_backup:
                    print(f"    2) Verifica Integrità superata: '{file_backup}' e '{file_standard}' coincidono ({dim_backup} byte).")
                else:
                    print(f"    ❌ Errore critico al Passo 2: Dimensione del backup non corrispondente! Interrompo il programma.")
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

# --- ESECUZIONE DIRETTA ---
if __name__ == "__main__":
    # Quando chiami la procedura passando il nome della pagina come stringa, 
    # viene eseguita immediatamente senza fare alcuna domanda a schermo.
    
    elabora_pagina_turismo('carracci')