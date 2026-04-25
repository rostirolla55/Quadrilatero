import os
import json
import re

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def update_all_html_menus(root_path="."):
    languages = ['it', 'en', 'es', 'fr']
    menu_html_by_lang = {}

    print("--- Inizio aggiornamento menu Nav ---")

    # 1. Pre-generiamo i blocchi HTML del menu per ogni lingua
    for lang in languages:
        texts_path = os.path.join(root_path, 'data', 'translations', lang, 'texts.json')
        nav_json_path = os.path.join(root_path, 'menu_json', f'nav-{lang}.json')
        
        texts_data = load_json(texts_path)
        nav_structure = load_json(nav_json_path)

        if not texts_data or not nav_structure:
            print(f" [!] Salto lingua {lang.upper()}: file JSON mancanti.")
            continue

        nav_translations = texts_data.get('nav', {})
        items = nav_structure.get('items', [])

        # Costruiamo il blocco HTML
        new_menu_html = '     <ul>\n'
        for item in items:
            nav_id = item.get('id', '')
            href = item.get('href', '#')
            # Prende la traduzione da texts.json, se manca usa il testo nel nav.json
            text = nav_translations.get(nav_id, item.get('text', 'Link'))
            
            new_menu_html += f'      <li>\n'
            new_menu_html += f'       <a href="{href}" id="{nav_id}">\n'
            new_menu_html += f'        {text}\n'
            new_menu_html += f'       </a>\n'
            new_menu_html += f'      </li>\n'
        new_menu_html += '     </ul>'
        
        menu_html_by_lang[lang] = new_menu_html

    # 2. Iteriamo su TUTTI i file HTML nella cartella
    for filename in os.listdir(root_path):
        if not filename.endswith('.html'):
            continue

        filepath = os.path.join(root_path, filename)
        
        # DETERMINA LA LINGUA DEL FILE
        # Se il file contiene il suffisso lo usiamo, altrimenti DEFAULT = IT
        file_lang = 'it' 
        if filename.endswith('-en.html'): file_lang = 'en'
        elif filename.endswith('-es.html'): file_lang = 'es'
        elif filename.endswith('-fr.html'): file_lang = 'fr'
        elif filename.endswith('-it.html'): file_lang = 'it'
        # Nota: se il file è 'manifattura.html' o 'index.html', file_lang resta 'it'

        if file_lang not in menu_html_by_lang:
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 3. SOSTITUZIONE DEL BLOCCO NAV
        # Cerchiamo l'ul dentro il div con classe nav-bar-content
        # Il pattern è studiato per essere molto tollerante agli spazi
        pattern = r'(<div class="nav-bar-content"[^>]*>\s*)<ul>.*?</ul>'
        replacement = r'\1' + menu_html_by_lang[file_lang]
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f" [OK] Aggiornato: {filename} (Lingua: {file_lang})")
        else:
            # Se il file non ha il blocco nav (es. un redirect puro), lo saltiamo senza errori
            if 'nav-bar-content' in content:
                print(f" [!] Blocco trovato ma identico in: {filename}")
            else:
                pass # File senza menu, ignorato silenziosamente

    print("--- Operazione completata ---")

if __name__ == "__main__":
    # Assicurati di essere nella root corretta
    update_all_html_menus(".")