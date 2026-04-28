import os
import json
import re

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def generate_gps_blocks(pois):
    """Genera i blocchi JS per le coordinate GPS"""
    loc_js = "const POIS_LOCATIONS = [\n"
    for i, p in enumerate(pois):
        sep = "," if i < len(pois) - 1 else ""
        loc_js += f"    {{ id: '{p['id']}', lat: {p['lat']}, lon: {p['lon']}, distanceThreshold: {p['threshold']}, categoria: '{p['categoria']}' }}{sep}\n"
    loc_js += "];"

    nav_links_js = "const navLinksData = {\n"
    for i, p in enumerate(pois):
        sep = "," if i < len(pois) - 1 else ""
        nav_links_js += f"    '{p['nav_id']}': '{p['id']}'{sep}\n"
    nav_links_js += "};"
    
    return loc_js, nav_links_js

def update_all_files():
    root_path = "."
    languages = ['it', 'en', 'es', 'fr']
    
    # 1. Carichiamo la configurazione GPS
    pois_data = load_json('pois_config.json')
    pois = pois_data.get('pois', []) if pois_data else []
    loc_js, nav_links_js = generate_gps_blocks(pois)

    # 2. Pre-generiamo i menu HTML per ogni lingua
    menu_blocks = {}
    for lang in languages:
        nav_json = load_json(os.path.join('menu_json', f'nav-{lang}.json'))
        if nav_json:
            items = nav_json.get('items', [])
            html = '     <ul>\n'
            for item in items:
                html += f'      <li>\n       <a href="{item["href"]}" id="{item["id"]}">{item["text"]}</a>\n      </li>\n'
            html += '     </ul>'
            menu_blocks[lang] = html

    print("--- Inizio Aggiornamento Totale HTML ---")

    # 3. Scansione di TUTTI i file HTML
    for filename in os.listdir(root_path):
        if not filename.endswith('.html'):
            continue

        filepath = os.path.join(root_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Determina la lingua: se non c'è suffisso, è Italiano (Redirect)
        is_redirect = True
        lang = 'it'
        if filename.endswith('-en.html'): lang = 'en'; is_redirect = False
        elif filename.endswith('-es.html'): lang = 'es'; is_redirect = False
        elif filename.endswith('-fr.html'): lang = 'fr'; is_redirect = False
        elif filename.endswith('-it.html'): lang = 'it'; is_redirect = False

        # AGGIORNAMENTO MENU (navBarMain)
        if lang in menu_blocks:
            pattern_nav = r'(<div class="nav-bar-content"[^>]*>\s*)<ul>.*?</ul>'
            content = re.sub(pattern_nav, r'\1' + menu_blocks[lang], content, flags=re.DOTALL)

        # AGGIORNAMENTO GPS (Solo se è un file di reindirizzamento)
        if is_redirect:
            if "const POIS_LOCATIONS" in content:
                content = re.sub(r"const POIS_LOCATIONS = \[.*?\];", loc_js, content, flags=re.DOTALL)
                content = re.sub(r"const navLinksData = \{.*?\};", nav_links_js, content, flags=re.DOTALL)

        # Salvataggio se ci sono state modifiche
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        type_str = "(Redirect + Menu)" if is_redirect else f"(Menu {lang.upper()})"
        print(f" [OK] {filename} {type_str}")

    print("--- Fine Operazione ---")

if __name__ == "__main__":
    update_all_files()