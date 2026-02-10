import json
import os

def sync_nav_from_config():
    config_file = "pois_config.json"
    output_dir = "menu_json"
    
    if not os.path.exists(config_file):
        print(f"Errore: {config_file} non trovato!")
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    pois = config.get("pois", [])
    languages = ["it", "en", "es", "fr"]
    
    home_labels = {"it": "Home", "en": "Home", "es": "Inicio", "fr": "Accueil"}

    for lang in languages:
        items = []
        # Home
        items.append({
            "id": "navHome",
            "href": "index-it.html" if lang == "it" else f"index-{lang}.html",
            "text": home_labels[lang]
        })

        # POIs
        for poi in pois:
            base = poi.get("base_name", "")
            href = f"{base}-it.html" if lang == "it" else f"{base}-{lang}.html"
            text = poi.get("label", {}).get(lang, poi.get("title", "Link"))
            
            items.append({
                "id": poi.get("nav_id", ""),
                "href": href,
                "text": text
            })

        output_path = os.path.join(output_dir, f"nav-{lang}.json")
        with open(output_path, 'w', encoding='utf-8') as jf:
            json.dump(items, jf, ensure_ascii=False, indent=4)
        print(f"Generato {output_path} con {len(items)} voci.")

if __name__ == "__main__":
    sync_nav_from_config()