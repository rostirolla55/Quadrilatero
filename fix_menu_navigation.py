import os
import json
from bs4 import BeautifulSoup

def fix_menu_navigation():
    # Carichiamo la configurazione originale dei POI
    config_file = "pois_config.json"
    if not os.path.exists(config_file):
        print("Configurazione non trovata!")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    pois = config.get("pois", [])
    
    # Per ogni lingua, aggiorniamo i file HTML corrispondenti
    for lang in ['it', 'en', 'es', 'fr']:
        suffix = f"-{lang}.html"
        html_files = [f for f in os.listdir('.') if f.endswith(suffix)]
        
        for filename in html_files:
            with open(filename, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            
            nav = soup.find('nav', id='navBarMain')
            if not nav: continue
            
            changed = False
            links = nav.find_all('a')
            for a in links:
                nav_id = a.get('id', '')
                # Cerchiamo il POI corrispondente a questo ID nel menu
                for poi in pois:
                    if poi.get('nav_id') == nav_id:
                        base = poi.get('base_name')
                        target_href = f"{base}-{lang}.html"
                        if a.get('href') != target_href:
                            a['href'] = target_href
                            changed = True
            
            if changed:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(soup.prettify(formatter="html"))
                print(f"Menu corretto per: {filename}")

if __name__ == "__main__":
    fix_menu_navigation()