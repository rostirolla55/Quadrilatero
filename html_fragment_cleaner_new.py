import os
import re

FRAGMENTS_DIR = "text_files"

def clean_html_fragment(html_content: str) -> str:
    """
    Pulisce il contenuto HTML rimuovendo intestazioni complete (DOCTYPE, head, body),
    tag <img> spuri di LibreOffice e incapsulando il corpo rimanente in UN UNICO div.
    """
    if not html_content.strip():
        return ""

    # 1. Rimuovi DOCTYPE e blocchi HEAD (tutto prima di <body>)
    body_match = re.search(r'<body[^>]*>(.*)', html_content, re.DOTALL | re.IGNORECASE)
    clean_content = body_match.group(1).strip() if body_match else html_content.strip()

    # 2. Rimuovi i tag </body> e </html> rimanenti
    clean_content = re.sub(r'</body[^>]*>\s*</html>\s*$', '', clean_content, flags=re.IGNORECASE | re.DOTALL).strip()
    
    # 3. RIMOZIONE TAG <IMG> SPURI DI LIBREOFFICE (Elimina gli errori 404)
    clean_content = re.sub(r'<img[^>]+src=["\'][^"\']*_html_[^"\']*["\'][^>]*>', '', clean_content, flags=re.IGNORECASE)

    # 4. RIMOZIONE DIV MAIN-TEXT-CONTENT ESISTENTI (PULIZIA NIDIFICAZIONI VECCHIE)
    clean_content = re.sub(r'<div\s+class=["\']main-text-content["\']\s*>', '', clean_content, flags=re.IGNORECASE)
    
    while clean_content.endswith('</div>'):
        clean_content = clean_content[:-6].strip()

    clean_content = clean_content.strip()
    if not clean_content:
        return ""

    # 5. Aggiungi UN SOLO contenitore radice pulito
    return f'<div class="main-text-content">\n{clean_content}\n</div>'

def process_fragments(directory: str):
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
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            processed_count += 1
        except Exception as e:
            print(f"  - ERRORE durante la pulizia di {filename}: {e}")

    print(f"✅ Pulizia completata. {processed_count} file processati.")

if __name__ == "__main__":
    process_fragments(FRAGMENTS_DIR)