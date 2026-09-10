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
    """
    trans = get_translations(title_it)
    
    for lang in LANGUAGES:
        # 1. Aggiornamento dei file texts.json
        texts_path = os.path.join(root, "data", "translations", lang, "texts.json")
        if os.path.exists(texts_path):
            try:
                with open(texts_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
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

        # 2. Aggiornamento dei file nav-*.json
        nav_json_path = os.path.join(root, "menu_json", f"nav-{lang}.json")
        if os.path.exists(nav_json_path):
            try:
                with open(nav_json_path, "r", encoding="utf-8") as f:
                    nav_content = json.load(f)
                
                if isinstance(nav_content, list):
                    nav_content = {"items": nav_content}
                
                if "items" not in nav_content:
                    nav_content["items"] = []

                if not any(item.get('id') == nav_key_id for item in nav_content["items"]):
                    # Il link nel menu punta sempre alla versione specifica per lingua
                    href = f"{page_id}-{lang}.html"
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
    if len(sys.argv) < 8:
        print("Errore: Parametri insufficienti per add_page.py")
        return

    page_id = sys.argv[1]
    nav_key_id = sys.argv[2]
    title = sys.argv[3]
    root = sys.argv[7].strip('"')

    # Aggiorna database testi e menu JSON
    update_texts_and_nav_json(root, page_id, nav_key_id, title)
    
    # 1. Creazione dei 4 file con suffisso (it, en, es, fr)
    # Questi usano i template specifici per lingua
    for lang in LANGUAGES:
        filename = f"{page_id}-{lang}.html"
        target_path = os.path.join(root, filename)
        
        if not os.path.exists(target_path):
            template_name = f"template-{lang}.html"
            template_path = os.path.join(root, template_name)
            
            if os.path.exists(template_path):
                shutil.copy(template_path, target_path)
                print(f" [+] Creato file lingua: {filename}")
            else:
                # Fallback sul template-it se manca quello specifico
                template_it = os.path.join(root, "template-it.html")
                if os.path.exists(template_it):
                    shutil.copy(template_it, target_path)
                    print(f" [!] Creato {filename} usando template-it.html")

    # 2. Creazione del file "Redirect" senza suffisso (es: manifattura.html)
    # Questo file non ha il tag Google Analytics e serve da ingresso principale
    redirect_filename = f"{page_id}.html"
    redirect_target = os.path.join(root, redirect_filename)
    
    if not os.path.exists(redirect_target):
        # Cerca un template specifico per il redirect, altrimenti usa quello base
        template_redir = os.path.join(root, "template-redirect.html")
        if not os.path.exists(template_redir):
            template_redir = os.path.join(root, "template.html")
            
        if os.path.exists(template_redir):
            shutil.copy(template_redir, redirect_target)
            print(f" [+] Creato file redirect principale: {redirect_filename}")
        else:
            print(f" [!] ATTENZIONE: Impossibile creare {redirect_filename}, template-redirect.html non trovato.")

if __name__ == "__main__":
    main()