import os
import re
from bs4 import BeautifulSoup

def fix_sancarlo_language_links():
    # Directory principale
    root_path = os.getcwd()
    
    # Lista dei file da controllare
    files_to_fix = [
        "chiesasancarlo-it.html",
        "chiesasancarlo-en.html",
        "chiesasancarlo-es.html",
        "chiesasancarlo-fr.html",
        "chiesasancarlo.html" # Se esiste la versione base
    ]

    # Mappa delle lingue e dei relativi file corretti
    lang_map = {
        "it": "chiesasancarlo-it.html",
        "en": "chiesasancarlo-en.html",
        "es": "chiesasancarlo-es.html",
        "fr": "chiesasancarlo-fr.html"
    }

    for filename in files_to_fix:
        file_path = os.path.join(root_path, filename)
        
        if not os.path.exists(file_path):
            continue

        print(f"Analisi di {filename}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Cerchiamo il selettore di lingua. 
        # Di solito è un div con classe 'language-selector' o simili, 
        # contenente link con immagini delle bandiere.
        links_found = 0
        all_links = soup.find_all('a')
        
        for a in all_links:
            href = a.get('href', '')
            img = a.find('img')
            
            # Identifichiamo i link delle lingue tramite l'immagine o l'href
            if img and ('flag' in img.get('src', '').lower() or 'lang' in img.get('alt', '').lower()):
                # Determiniamo la lingua di destinazione basandoci sull'immagine o testo
                alt_text = img.get('alt', '').lower()
                
                target_lang = None
                if 'it' in alt_text or 'italiano' in alt_text or 'italy' in alt_text:
                    target_lang = 'it'
                elif 'en' in alt_text or 'english' in alt_text or 'uk' in alt_text:
                    target_lang = 'en'
                elif 'es' in alt_text or 'spanish' in alt_text or 'spagna' in alt_text:
                    target_lang = 'es'
                elif 'fr' in alt_text or 'french' in alt_text or 'francia' in alt_text:
                    target_lang = 'fr'

                if target_lang:
                    old_href = a['href']
                    new_href = lang_map[target_lang]
                    if old_href != new_href:
                        a['href'] = new_href
                        links_found += 1
                        print(f"  -> Corretto link {target_lang}: {old_href} -> {new_href}")

        if links_found > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(soup.prettify(formatter="html"))
            print(f" [+] Salvato {filename} con {links_found} correzioni.")
        else:
            print(f" [!] Nessuna correzione necessaria per {filename}.")

if __name__ == "__main__":
    fix_sancarlo_language_links()