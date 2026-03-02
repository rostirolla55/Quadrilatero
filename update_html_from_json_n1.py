import os
import json
import re

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def update_all_html_menus(root_path):
    languages = ['it', 'en', 'es', 'fr']
    
    for lang in languages:
        # 1. Carichiamo la sorgente della verità (texts.json)
        texts_path = os.path.join(root_path, 'data', 'translations', lang, 'texts.json')
        texts_data = load_json(texts_path)
        if not texts_data or 'nav' not in texts_data:
            print(f" [!] Salto {lang}: texts.json non trovato o senza sezione 'nav'")
            continue
            
        nav_translations = texts_data['nav']

        # 2. Carichiamo la struttura del menu (nav-*.json)
        nav_json_path = os.path.join(root_path, 'menu_json', f'nav-{lang}.json')
        nav_structure = load_json(nav_json_path)
        if not nav_structure:
            continue

        # Costruiamo il nuovo blocco HTML del menu basandoci sui testi corretti
        items = nav_structure.get('items', [])
        new_menu_html = '     <ul>\n'
        for item in items:
            nav_id = item.get('id', '')
            href = item.get('href', '#')
            # Cerchiamo il testo in texts.json usando l'ID, altrimenti fallback
            text = nav_translations.get(nav_id, item.get('text', 'Link'))
            
            new_menu_html += f'      <li>\n'
            new_menu_html += f'       <a href="{href}" id="{nav_id}">\n'
            new_menu_html += f'        {text}\n'
            new_menu_html += f'       </a>\n'
            new_menu_html += f'      </li>\n'
        new_menu_html += '     </ul>'

        # 3. Aggiorniamo tutti i file HTML di quella lingua
        suffix = f"-{lang}.html"
        for filename in os.listdir(root_path):
            if filename.endswith(suffix):
                filepath = os.path.join(root_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Regex per trovare il blocco <ul>...</ul> dentro il navBarMain
                # Cerca l'ul all'interno della div nav-bar-content
                pattern = r'(<div class="nav-bar-content"[^>]*>\s*)<ul>.*?</ul>'
                replacement = r'\1' + new_menu_html
                
                new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f" [+] Aggiornato menu in: {filename} ({lang})")

if __name__ == "__main__":
    # Assumiamo che lo script sia nella root del progetto
    update_all_html_menus(os.getcwd())