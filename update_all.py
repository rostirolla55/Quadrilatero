import os
import json
from bs4 import BeautifulSoup

def update_all():
    json_folder = "menu_json"
    root_path = os.getcwd()

    for lang in ["it", "en", "es", "fr"]:
        json_path = os.path.join(json_folder, f"nav-{lang}.json")
        if not os.path.exists(json_path): continue
        
        with open(json_path, 'r', encoding='utf-8') as f:
            menu_items = json.load(f)

        # Cerca tutti i file relativi a questa lingua
        suffix = f"-{lang}.html"
        files = [f for f in os.listdir(root_path) if f.endswith(suffix)]
        
        for html_file in files:
            with open(html_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            
            nav = soup.find('nav', id='navBarMain')
            if nav:
                nav.clear()
                content_div = soup.new_tag('div', attrs={'class': 'nav-bar-content'})
                ul = soup.new_tag('ul')
                for item in menu_items:
                    li = soup.new_tag('li')
                    a = soup.new_tag('a', attrs={'href': item['href'], 'id': item['id']})
                    a.string = item['text']
                    li.append(a)
                    ul.append(li)
                content_div.append(ul)
                nav.append(content_div)
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(soup.prettify(formatter="html"))
                print(f"Menu aggiornato in {html_file}")

if __name__ == "__main__":
    update_all()