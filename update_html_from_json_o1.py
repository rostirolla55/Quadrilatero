import os
import re
import json
from bs4 import BeautifulSoup

def update_html_from_json():
    """
    Aggiorna i file HTML inserendo il menu aggiornato dai file JSON.
    Gestisce sia il formato {'items': [...]} che il formato lista [...].
    """
    root_path = os.getcwd()
    json_folder = os.path.join(root_path, "menu_json")
    lang_pattern = re.compile(r'-([a-z]{2})\.html$')
    
    if not os.path.exists(json_folder):
        print(f"Errore: La cartella '{json_folder}' non esiste.")
        return

    # 1. Caricamento dei JSON
    menu_data = {}
    json_files = [f for f in os.listdir(json_folder) if f.startswith("nav-") and f.endswith(".json")]
    
    for jf_name in json_files:
        lang_code = jf_name.replace("nav-", "").replace(".json", "")
        try:
            with open(os.path.join(json_folder, jf_name), 'r', encoding='utf-8') as f:
                content = json.load(f)
                # Normalizzazione: vogliamo sempre una lista di items
                if isinstance(content, dict):
                    menu_data[lang_code] = content.get('items', [])
                elif isinstance(content, list):
                    menu_data[lang_code] = content
                else:
                    menu_data[lang_code] = []
                print(f"Caricato menu {lang_code}: {len(menu_data[lang_code])} voci.")
        except Exception as e:
            print(f"Errore caricamento {jf_name}: {e}")

    # 2. Scansione HTML
    for html_name in os.listdir(root_path):
        if not html_name.endswith(".html"):
            continue
            
        file_path = os.path.join(root_path, html_name)
        match = lang_pattern.search(html_name)
        lang = match.group(1) if match else "it"

        if lang not in menu_data:
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            nav_tag = soup.find('nav', id='navBarMain')
            if nav_tag:
                # Pulizia contenuto precedente
                nav_tag.clear()
                
                # Creazione struttura: div class="nav-bar-content" -> ul
                nav_content_div = soup.new_tag('div', attrs={'class': 'nav-bar-content'})
                ul = soup.new_tag('ul')
                
                for item in menu_data[lang]:
                    li = soup.new_tag('li')
                    # Gestione attributi link
                    a_attrs = {'href': item.get('href', '#')}
                    if 'id' in item and item['id']:
                        a_attrs['id'] = item['id']
                    
                    a = soup.new_tag('a', attrs=a_attrs)
                    a.string = item.get('text', 'Link')
                    li.append(a)
                    ul.append(li)
                
                nav_content_div.append(ul)
                nav_tag.append(nav_content_div)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Usiamo formatter="html" per mantenere i caratteri speciali corretti
                    f.write(soup.prettify(formatter="html"))
                print(f"OK: {html_name} aggiornato.")
            else:
                print(f"AVVISO: {html_name} non ha <nav id='navBarMain'>")
                
        except Exception as e:
            print(f"Errore su {html_name}: {e}")

if __name__ == "__main__":
    update_html_from_json()