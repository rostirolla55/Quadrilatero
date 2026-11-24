import json
import os

TRANSLATIONS_DIR = "data/translations"
LINGUE = ["it", "en", "es", "fr"]
CHIAVI_DETT = [
    "dettText1", "dettText2", "dettText3", "dettText4", "dettText5",
    "imageDett1", "imageDett2", "imageDett3", "imageDett4", "imageDett5",
]

def pulisci_texts_json(dry_run: bool = True):
    for lang in LINGUE:
        path = os.path.join(TRANSLATIONS_DIR, lang, "texts.json")
        if not os.path.exists(path):
            print(f"[SKIP] Non trovato: {path}")
            continue

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        rimosse_tot = 0
        for blocco_id, blocco in data.items():
            if not isinstance(blocco, dict):
                continue
            if "_dett_" in blocco_id.lower():
                continue

            for chiave in CHIAVI_DETT:
                if chiave in blocco:
                    if not dry_run:
                        del blocco[chiave]
                    rimosse_tot += 1

        print(f"[{lang}] Chiavi dettaglio {'da rimuovere' if dry_run else 'rimosse'}: {rimosse_tot} ({path})")

        if not dry_run and rimosse_tot > 0:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # Prima prova con dry_run=True per vedere i numeri, poi metti dry_run=False
    pulisci_texts_json(dry_run=False)