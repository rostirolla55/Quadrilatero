import os
import re

# Directory dove si trovano i file HTML sporchi
TEXT_FILES_DIR = "text_files"

def clean_html_content(file_path):
    """
    Rimuove i tag <div class="main-text-content"> nidificati in eccesso,
    lasciandone solo uno esterno o rimuovendoli del tutto se preferito.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern per trovare l'apertura del div specifico
    opening_tag = '<div class="main-text-content">'
    closing_tag = '</div>'

    # Conta quante volte appare il tag di apertura
    count_open = content.count(opening_tag)
    
    if count_open <= 1:
        return False # Nessuna pulizia necessaria

    print(f"Pulizia di {file_path}: trovati {count_open} tag nidificati.")

    # Rimuoviamo TUTTE le istanze del tag di apertura e chiusura specifico
    # per poi avvolgere il contenuto in un unico div pulito alla fine.
    cleaned_body = content.replace(opening_tag, "")
    cleaned_body = cleaned_body.replace(closing_tag, "")
    
    # Rimuoviamo eventuali spazi bianchi o newline superflue all'inizio e alla fine
    cleaned_body = cleaned_body.strip()

    # Ricostruiamo la struttura corretta con un solo contenitore
    final_content = f'<div class="main-text-content">\n{cleaned_body}\n</div>'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    return True

def process_directory():
    if not os.path.exists(TEXT_FILES_DIR):
        print(f"Errore: la cartella {TEXT_FILES_DIR} non esiste.")
        return

    files = [f for f in os.listdir(TEXT_FILES_DIR) if f.endswith('.html')]
    modified_count = 0

    for filename in files:
        file_path = os.path.join(TEXT_FILES_DIR, filename)
        if clean_html_content(file_path):
            modified_count += 1

    print(f"\nOperazione completata. File ripuliti: {modified_count}")

if __name__ == "__main__":
    process_directory()