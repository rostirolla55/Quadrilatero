import os
import re
from bs4 import BeautifulSoup

def fix_all_languages_nav():
    root_path = os.getcwd()
    # Cerchiamo tutti i file che hanno un suffisso di lingua (es: -en.html, -it.html)
    lang_file_pattern = re.compile(r'-(en|it|fr|es)\.html$')
    
    files = [f for f in os.listdir(root_path) if lang_file_pattern.search(f)]

    for filename in files:
        # Estraiamo la lingua dal nome del file (es: "en")
        match = lang_file_pattern.search(filename)
        lang_suffix = match.group(1)
        
        file_path = os.path.join(root_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        nav_tag = soup.find('nav', id='navBarMain')
        if not nav_tag:
            continue

        updated = False
        for a in nav_tag.find_all('a'):
            href = a.get('href', '')
            
            # Se il link è un file .html e NON ha già il suffisso della lingua corrente
            if href.endswith('.html') and f'-{lang_suffix}.html' not in href:
                # Esempio: index.html -> index-en.html
                new_href = href.replace('.html', f'-{lang_suffix}.html')
                a['href'] = new_href
                updated = True
        
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(soup.prettify(formatter="html"))
            print(f"[*] Aggiornati link in {filename} per lingua: {lang_suffix}")

if __name__ == "__main__":
    fix_all_languages_nav()