import json
import os
# ripara i files nav-xx.json nella directory menu_json
# i files aggiornati tramite update_html_from_json.py correggono i file html
def fix_nav():
    json_folder = "menu_json"
    # Definiamo i titoli corretti per le varie lingue
    titles = {
        "it": "Chiesa San Carlo Borromeo del Porto",
        "en": "Church of St. Charles Borromeo",
        "es": "Iglesia de San Carlos Borromeo",
        "fr": "Église Saint-Charles-Borromée"
    }
    
    target_id = "navChiesaSancarlo"

    for lang in ["it", "en", "es", "fr"]:
        file_path = os.path.join(json_folder, f"nav-{lang}.json")
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Gestiamo sia il formato lista che il formato oggetto {'items': []}
        items = data.get('items', []) if isinstance(data, dict) else data
        
        updated = False
        for item in items:
            if item.get('id') == target_id:
                item['text'] = titles[lang]
                updated = True
        
        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f" [+] Titolo aggiornato in {file_path}")

if __name__ == "__main__":
    fix_nav()