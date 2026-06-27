import os
import re
from docx import Document

# Configurazione percorsi
SOURCE_DIR = r"C:\Users\User\Documents\GitHub\Quadrilatero\DOCS_DA_CONVERTIRE"
OUTPUT_FILE = os.path.join(SOURCE_DIR, "quad_blocco_immagini_generato.txt")

# Regex fornita per intercettare il tag e catturare il nome dell'immagine
SPLIT_BLOCK_PATTERN = r'\[SPLIT_BLOCK:\s*(.+?\.(?:jpg|jpeg|png|gif|bmp))\]'

def estrai_righe_formattate():
    if not os.path.exists(SOURCE_DIR):
        print(f"Errore: La directory {SOURCE_DIR} non esiste.")
        return

    testo_output = ""
    compiled_regex = re.compile(SPLIT_BLOCK_PATTERN)
    tutti_i_file = os.listdir(SOURCE_DIR)

    for filename in tutti_i_file:
        # Salta i file temporanei di Word
        if filename.startswith("~$"):
            continue
            
        # Filtra i file -it.docx
        if filename.lower().endswith("_it.docx"):
            file_path = os.path.join(SOURCE_DIR, filename)
            
            try:
                doc = Document(file_path)
                tag_del_file = []
                
                # Cerca i tag in tutti i paragrafi del documento
                for paragraph in doc.paragraphs:
                    riga = paragraph.text.strip()
                    
                    if compiled_regex.search(riga):
                        # Salviamo la riga intera così come si presenta (es. [SPLIT_BLOCK:immagine.jpg])
                        tag_del_file.append(riga)
                
                # Se abbiamo trovato almeno un tag in questo file, creiamo il blocco nel report
                if tag_del_file:
                    # Pulisce il nome del file per farlo diventare l'intestazione (ID della pagina)
                    # Toglie '-it.docx' o '-it.DOCX' alla fine
                    nome_pagina = filename[:-8] 
                    # Sostituisce eventuali trattini con underscore se preferisci quel formato
                    nome_pagina = nome_pagina.replace("-", "_")
                    
                    # Costruisce la sezione per questo file
                    testo_output += f"{nome_pagina}:\n"
                    for tag in tag_del_file:
                        testo_output += f"{tag}\n"
                        
            except Exception as e:
                print(f"Errore durante la lettura del file {filename}: {e}")

    # Scrittura del file finale nel formato desiderato
    if testo_output:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(testo_output)
        print(f"File generato con successo in: {OUTPUT_FILE}")
        print("\nAnteprima dell'output generato:")
        print("-" * 30)
        print(testo_output)
        print("-" * 30)
    else:
        print("Nessun tag corrispondente trovato. Il file di output non è stato generato.")

if __name__ == "__main__":
    estrai_righe_formattate()