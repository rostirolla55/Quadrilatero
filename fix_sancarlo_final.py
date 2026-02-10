import os
import re

def force_fix_sancarlo():
    # Definiamo la mappa dei file reali per ogni lingua
    pages = {
        "it": "chiesasancarlo-it.html",
        "en": "chiesasancarlo-en.html",
        "es": "chiesasancarlo-es.html",
        "fr": "chiesasancarlo-fr.html"
    }

    print("Inizio riparazione forzata link lingue...")

    for current_lang, filename in pages.items():
        if not os.path.exists(filename):
            print(f" [!] File saltato (non esiste): {filename}")
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        modified = False
        
        # Cerchiamo i blocchi link dentro language-selector
        # Esempio: <a data-lang="it" href="index.html">
        for target_lang, target_file in pages.items():
            # Regex che cerca il link con quel data-lang specifico
            # cattura href="qualunque_cosa"
            pattern = rf'data-lang="{target_lang}"\s+href="[^"]+"'
            replacement = f'data-lang="{target_lang}" href="{target_file}"'
            
            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    modified = True
                    print(f"  [{filename}] Link {target_lang} corretto -> {target_file}")

        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f" [+] Salvato: {filename}")
        else:
            print(f" [-] Nessuna modifica necessaria per {filename}")

if __name__ == "__main__":
    force_fix_sancarlo()