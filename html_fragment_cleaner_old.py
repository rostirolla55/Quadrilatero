import os
import re
from typing import List

# Configurazione (deve corrispondere alla cartella di input del key_synchronization_v2.py)
FRAGMENTS_DIR = "text_files"

def clean_html_fragment(html_content: str) -> str:
    """
    Pulisce il contenuto HTML rimuovendo intestazioni complete (DOCTYPE, head, body)
    e incapsulando il corpo rimanente in UN UNICO div contenitore.
    """
    if not html_content.strip():
        return ""

    # 1. Rimuovi DOCTYPE e blocchi HEAD (tutto prima di <body>)
    body_match = re.search(r'<body[^>]*>(.*)', html_content, re.DOTALL | re.IGNORECASE)
    
    if body_match:
        clean_content = body_match.group(1).strip()
    else:
        clean_content = html_content.strip()

    # 2. Rimuovi i tag </body> e </html> rimanenti alla fine
    clean_content = re.sub(r'</body[^>]*>\s*</html>\s*$', '', clean_content, flags=re.IGNORECASE | re.DOTALL).strip()
    
    # 3. RIMOZIONE DI TUTTI I DIV MAIN-TEXT-CONTENT ESISTENTI (PULIZIA NIDIFICAZIONI VECCHIE)
    # Rimuove le aperture <div class="main-text-content">
    clean_content = re.sub(r'<div\s+class=["\']main-text-content["\']\s*>', '', clean_content, flags=re.IGNORECASE)
    
    # Rimuove le chiusure </div> corrispondenti accumulate in fondo o nel testo
    # (Pulisce i </div> superflui mantenendo la struttura interna pulita)
    while clean_content.endswith('</div>'):
        clean_content = clean_content[:-6].strip()

    clean_content = clean_content.strip()
    if not clean_content:
        return ""

    # 4. Aggiungi UN SOLO contenitore radice pulito per l'iniezione
    final_fragment = f'<div class="main-text-content">\n{clean_content}\n</div>'
    
    return final_fragment

def process_fragments(directory: str):
    """
    Scorre la directory e pulisce tutti i file HTML che potrebbero essere frammenti.
    """
    print(f"Inizio pulizia dei frammenti HTML nella directory: {directory}")
    processed_count = 0
    
    html_files = [f for f in os.listdir(directory) if f.endswith(".html")]
    
    if not html_files:
        print("Nessun file HTML trovato da pulire.")
        return

    for filename in html_files:
        filepath = os.path.join(directory, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            cleaned_content = clean_html_fragment(original_content)
            
            # Scrivi il contenuto pulito sullo stesso file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            print(f"  - Pulito e aggiornato: {filename}")
            processed_count += 1
            
        except Exception as e:
            print(f"  - ERRORE durante la pulizia di {filename}: {e}")

    print(f"✅ Pulizia completata. {processed_count} file processati.")

if __name__ == "__main__":
    process_fragments(FRAGMENTS_DIR)