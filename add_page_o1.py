import sys
import os
import json
import shutil

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ["it", "en", "es", "fr"]

def get_translations(title_it):
    """Genera traduzioni automatiche semplici per i titoli delle pagine."""
    mapping = {
        "Basilica": {"en": "Basilica", "es": "Basílica", "fr": "Basilique"},
        "Chiesa": {"en": "Church", "es": "Iglesia", "fr": "Église"},
        "Santa": {"en": "Saint", "es": "San", "fr": "Saint"},
        "Santo": {"en": "Saint", "es": "San", "fr": "Saint"},
        "San": {"en": "Saint", "es": "San", "fr": "Saint"},
    }
    translations = {"it": title_it}
    for lang in ["en", "es", "fr"]:
        trans = title_it
        for k, v in mapping.items():
            if k in trans:
                trans = trans.replace(k, v[lang])
        translations[lang] = trans
    return translations

def update_texts_and_nav_json(root, page_id, nav_key_id, title_it):
    """
    Aggiorna i file texts.json e i menu JSON (nav-*.json).
    Si assicura che la struttura dei menu sia {"items": [...]} per la compatibilità.
    """
    trans = get_translations(title_it)
    
    for lang in LANGUAGES:
        # 1. Aggiornamento dei file texts.json (Contenuti testuali della pagina)
        texts_path = os.path.join(root, "data", "translations", lang, "texts.json")
        if os.path.exists(texts_path):
            try:
                with open(texts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Aggiunge la pagina se non esiste già nelle traduzioni
                if page_id not in data:
                    data[page_id] = {
                        "pageTitle": trans[lang],
                        "headerTitle": trans[lang],
                        "mainText": f"Benvenuti a {trans[lang]}...",
                        "mainText1": "", "mainText2": "", "mainText3": "", "mainText4": "", "mainText5": ""
                    }
                    with open(texts_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    print(f" [+] Texts ({lang}) aggiornato per {page_id}")
            except Exception as e:
                print(f"Errore caricamento texts.json ({lang}): {e}")

        # 2. Aggiornamento dei file nav-*.json (Menu di navigazione)
        nav_json_path = os.path.join(root, "menu_json", f"nav-{lang}.json")
        if os.path.exists(nav_json_path):
            try:
                with open(nav_json_path, "r", encoding="utf-8") as f:
                    nav_content = json.load(f)
                
                # Normalizzazione: se il file è una lista [], lo trasformiamo in {"items": []}
                if isinstance(nav_content, list):
                    nav_content = {"items": nav_content}
                elif not isinstance(nav_content, dict):
                    nav_content = {"items": []}
                
                if "items" not in nav_content:
                    nav_content["items"] = []

                # Verifica se il link esiste già per evitare duplicati
                if not any(item.get('id') == nav_key_id for item in nav_content["items"]):
                    href = f"{page_id}.html" if lang == "it" else f"{page_id}-{lang}.html"
                    nav_content["items"].append({
                        "id": nav_key_id,
                        "href": href,
                        "text": trans[lang]
                    })
                    with open(nav_json_path, "w", encoding="utf-8") as f:
                        json.dump(nav_content, f, indent=4, ensure_ascii=False)
                    print(f" [+] Menu ({lang}) aggiornato con {nav_key_id}")
            except Exception as e:
                print(f"Errore aggiornamento menu JSON ({lang}): {e}")

def main():
    # Parametri attesi dal file .bat:
    # 1: page_id, 2: nav_key_id, 3: title, 4: lat, 5: lon, 6: dist, 7: root_path
    if len(sys.argv) < 8:
        print("Errore: Parametri insufficienti per add_page.py")
        return

    page_id = sys.argv[1]
    nav_key_id = sys.argv[2]
    title = sys.argv[3]
    root = sys.argv[7].strip('"')

    # Aggiorna database testi e menu JSON
    update_texts_and_nav_json(root, page_id, nav_key_id, title)
    
    # Creazione fisica dei file HTML partendo dai template se non esistono
    for lang in LANGUAGES:
        suffix = "" if lang == "it" else f"-{lang}"
        filename = f"{page_id}{suffix}.html"
        target_path = os.path.join(root, filename)
        
        if not os.path.exists(target_path):
            template_name = f"template-{lang}.html"
            template_path = os.path.join(root, template_name)
            
            if os.path.exists(template_path):
                shutil.copy(template_path, target_path)
                print(f" [+] Creato file: {filename}")
            else:
                # Se manca il template specifico, prova quello italiano
                template_it = os.path.join(root, "template-it.html")
                if os.path.exists(template_it):
                    shutil.copy(template_it, target_path)
                    print(f" [!] Creato {filename} usando template-it.html (mancava template-{lang})")

if __name__ == "__main__":
    main()