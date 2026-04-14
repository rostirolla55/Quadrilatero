import json
import os

def aggiorna_navigazione():
    # Configurazione lingue e percorsi
    lingue = ['it', 'en', 'es', 'fr']
    cartella_data = 'data/translations'
    cartella_menu = 'menu_json'

    for lang in lingue:
        # Percorsi dei file
        path_texts = os.path.join(cartella_data, lang, 'texts.json')
        path_nav = os.path.join(cartella_menu, f'nav-{lang}.json')

        # Verifica esistenza file
        if not os.path.exists(path_texts) or not os.path.exists(path_nav):
            print(f"[{lang.upper()}] Errore: File non trovati. Salto...")
            continue

        try:
            # 1. Carica le traduzioni (Sorgente)
            with open(path_texts, 'r', encoding='utf-8') as f:
                data_texts = json.load(f)
                mappa_nomi = data_texts.get("nav", {})

            # 2. Carica il menu (Destinazione)
            with open(path_nav, 'r', encoding='utf-8') as f:
                data_nav = json.load(f)

            # 3. Aggiorna i testi nel menu basandosi sull'ID
            contatore_modifiche = 0
            for item in data_nav.get("items", []):
                item_id = item.get("id")
                if item_id in mappa_nomi:
                    testo_nuovo = mappa_nomi[item_id]
                    if item["text"] != testo_nuovo:
                        item["text"] = testo_nuovo
                        contatore_modifiche += 1

            # 4. Salva il file aggiornato
            with open(path_nav, 'w', encoding='utf-8') as f:
                json.dump(data_nav, f, indent=4, ensure_ascii=False)

            print(f"[{lang.upper()}] Completato: {contatore_modifiche} voci aggiornate.")

        except Exception as e:
            print(f"[{lang.upper()}] Errore durante l'elaborazione: {e}")

if __name__ == "__main__":
    aggiorna_navigazione()