import os
import re
from bs4 import BeautifulSoup

def fix_language_links():
    # Estensioni e lingue gestite
    languages = ['it', 'en', 'es', 'fr']
    root_path = os.getcwd()
    
    # Cerchiamo tutti i file HTML nella cartella
    html_files = [f for f in os.listdir(root_path) if f.endswith('.html')]
    
    for filename in html_files:
        # Identifichiamo la base del file (es: "chiesasancarlo") e la lingua attuale
        match = re.search(r'^(.*?)-(it|en|es|fr)\.html$', filename)
        if not match:
            continue
            
        base_name = match.group(1)
        current_lang = match.group(2)
        
        changed = False
        with open(filename, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Cerchiamo tutti i link che contengono immagini (le bandiere)
        for a in soup.find_all('a'):
            img = a.find('img')
            if img:
                src = img.get('src', '').lower()
                alt = img.get('alt', '').lower()
                
                target_lang = None
                # Determiniamo la lingua di destinazione basandoci su alt o src dell'immagine
                if 'it' in alt or 'ital' in src: target_lang = 'it'
                elif 'en' in alt or 'engl' in src: target_lang = 'en'
                elif 'es' in alt or 'span' in src: target_lang = 'es'
                elif 'fr' in alt or 'fren' in src or 'fran' in src: target_lang = 'fr'
                
                if target_lang:
                    # Costruiamo il link corretto: base-lingua.html
                    # Esempio: chiesasancarlo-it.html
                    new_href = f"{base_name}-{target_lang}.html"
                    if a.get('href') != new_href:
                        a['href'] = new_href
                        changed = True

        if changed:
            with open(filename, 'w', encoding='utf-8') as f:
                # Usiamo formatter="html" per mantenere i tag puliti
                f.write(soup.prettify(formatter="html"))
            print(f"Sistemati link lingua in: {filename}")

if __name__ == "__main__":
    fix_language_links()