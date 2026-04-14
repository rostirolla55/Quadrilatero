import os
import re
import json
from bs4 import BeautifulSoup

def extract_nav_to_json(root_directory, output_directory="menu_json"):
    lang_pattern = re.compile(r'-([a-z]{2})\.html$')
    translations = {}

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(root_directory):
        if filename.endswith(".html"):
            file_path = os.path.join(root_directory, filename)
            match = lang_pattern.search(filename)
            lang_code = match.group(1) if match else "it"

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')

                # CERCA IL MENU: Prova prima per ID, poi per Classe
                nav_tag = soup.find('nav', id='navBarMain') or soup.find('nav', class_='nav-bar-main')
                
                if nav_tag:
                    items = []
                    links = nav_tag.find_all('a')
                    
                    for link in links:
                        # Estrae il testo e lo pulisce da spazi e ritorni a capo
                        testo_pulito = link.get_text(separator=" ", strip=True)
                        
                        item = {
                            "id": link.get('id', ''),
                            "href": link.get('href', '#'),
                            "text": testo_pulito
                        }
                        items.append(item)

                    # Salviamo i dati per questa lingua (usiamo l'ultimo file trovato per lingua)
                    if items:
                        translations[lang_code] = {"items": items}
                
            except Exception as e:
                print(f"Errore in {filename}: {e}")

    # Scrittura dei file JSON
    for lang, data in translations.items():
        output_file = os.path.join(output_directory, f"nav-{lang}.json")
        with open(output_file, 'w', encoding='utf-8') as jf:
            json.dump(data, jf, ensure_ascii=False, indent=4)
        print(f"Generato: {output_file}")

if __name__ == "__main__":
    # Esegui nella cartella corrente
    extract_nav_to_json(".", "menu_json")