import os
import re
import json
from bs4 import BeautifulSoup

def update_html_from_json():
    """
    Versione corretta: gestisce sia il formato {'items': []} che il formato [] (lista diretta).
    """
    root_path = os.getcwd()
    json_folder = os.path.join(root_path, "menu_json")
    lang_pattern = re.compile(r'-([a-z]{2})\\.html$')
    
    if not os.path.exists(json_folder): return

    menu_data = {}
    json_files = [f for f in os.listdir(json_folder) if f.startswith("nav-") and f.endswith(".json")]
    
    for jf_name in json_files:
        lang_code = jf_name.replace("nav-", "").replace(".json", "")
        with open(os.path.join(json_folder, jf_name), 'r', encoding='utf-8') as f:
            content = json.load(f)
            # Normalizzazione: se è una lista, la mettiamo sotto 'items'
            if isinstance(content, list):
                menu_data[lang_code] = {'items': content}
            else:
                menu_data[lang_code] = content

    for html_name in [f for f in os.listdir(root_path) if f.endswith(".html")]:
        match = lang_pattern.search(html_name)
        lang = match.group(1) if match else "it"
        
        if lang not in menu_data: continue
        
        file_path = os.path.join(root_path, html_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            nav_tag = soup.find('nav', id='navBarMain')
            if nav_tag:
                nav_tag.clear()
                nav_content_div = soup.new_tag('div', attrs={'class': 'nav-bar-content'})
                ul = soup.new_tag('ul')
                
                # Ora .get('items') non fallirà mai grazie alla normalizzazione sopra
                for item in menu_data[lang].get('items', []):
                    li = soup.new_tag('li')
                    a = soup.new_tag('a', href=item.get('href', '#'))
                    if 'id' in item: a['id'] = item['id']
                    a.string = item.get('text', '')
                    li.append(a)
                    ul.append(li)
                
                nav_content_div.append(ul)
                nav_tag.append(nav_content_div)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(soup.prettify(formatter="html"))
                print(f"OK: {html_name} aggiornato.")
        except Exception as e:
            print(f"Errore su {html_name}: {e}")

if __name__ == "__main__":
    update_html_from_json()