import json
import os

def sync_nav_from_config():
    """
    Legge pois_config.json e genera i file nav-xx.json completi
    per ogni lingua, includendo tutti i POI definiti.
    """
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
    
    # Etichette per la Home nelle varie lingue
    home_labels = {
        "it": "Home",
        "en": "Home",
        "es": "Inicio",
        "fr": "Accueil"
    }

    for lang in languages:
        items = []
        
        # 1. Aggiungi la Home (sempre prima)
        home_file = "index.html" if lang == "it" else f"index-{lang}.html"
        items.append({
            "id": "navHome",
            "href": home_file,
            "text": home_labels[lang]
        })

        # 2. Aggiungi tutti i POI dalla configurazione
        for poi in pois:
            # Determina il nome del file in base alla lingua
            # Se è 'it' il file è base.html, altrimenti base-lang.html
            base = poi.get("base_name", "")
            if lang == "it":
                href = f"{base}.html"
            else:
                href = f"{base}-{lang}.html"
            
            # Recupera la traduzione corretta per il testo del menu
            text = poi.get("label", {}).get(lang, poi.get("id", "Link"))
            
            items.append({
                "id": poi.get("nav_id", ""),
                "href": href,
                "text": text
            })

        # Salvataggio del file JSON per la lingua specifica
        output_path = os.path.join(output_dir, f"nav-{lang}.json")
        with open(output_path, 'w', encoding='utf-8') as jf:
            json.dump(items, jf, ensure_ascii=False, indent=4)
        
        print(f"Generato {output_path} con {len(items)} voci.")

if __name__ == "__main__":
    sync_nav_from_config()