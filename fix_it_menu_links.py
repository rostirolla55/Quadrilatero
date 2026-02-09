import os
import re
from bs4 import BeautifulSoup

def fix_it_menu_links():
    """
    Scansiona i file che terminano con '-it.html' e assicura che i link 
    dentro la navBarMain abbiano il suffisso '-it.html' (tranne casi particolari).
    """
    root_path = os.getcwd()
    
    # Cerchiamo tutti i file -it.html
    files_to_check = [f for f in os.listdir(root_path) if f.endswith("-it.html")]

    for filename in files_to_check:
        file_path = os.path.join(root_path, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        nav_tag = soup.find('nav', id='navBarMain')
        if not nav_tag:
            continue

        updated = False
        links = nav_tag.find_all('a')
        
        for a in links:
            href = a.get('href', '')
            
            # Se il link è un file .html e NON ha già -it.html
            if href.endswith('.html') and not href.endswith('-it.html'):
                # Caso speciale: index.html -> index-it.html
                # Caso generale: nome.html -> nome-it.html
                new_href = href.replace('.html', '-it.html')
                
                # Verifica se il file esiste prima di rinominare il link
                # (Opzionale, ma sicuro)
                a['href'] = new_href
                updated = True
                print(f"[{filename}] Corretto: {href} -> {new_href}")

        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(soup.prettify(formatter="html"))
            print(f" [+] Salvato: {filename}")

if __name__ == "__main__":
    fix_it_menu_links()