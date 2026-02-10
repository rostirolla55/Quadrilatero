import os
import re

def fix_sancarlo_ultra():
    # Mappa delle lingue e dei file corretti
    pages = {
        "it": "chiesasancarlo-it.html",
        "en": "chiesasancarlo-en.html",
        "es": "chiesasancarlo-es.html",
        "fr": "chiesasancarlo-fr.html"
    }

    print("--- Debug Inizio Riparazione ---")

    for current_lang, filename in pages.items():
        if not os.path.exists(filename):
            print(f" [!] File NON TROVATO: {filename}")
            continue

        print(f" Analisi di: {filename}...")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content
        found_any = False

        # Usiamo una regex molto permissiva per trovare i link data-lang
        # Cerca: <a ... data-lang="XX" ... href="YY" ... >
        # Il flag re.DOTALL permette di cercare su più righe
        pattern = re.compile(r'(<a[^>]*data-lang=["\'](?P<lang>it|en|es|fr)["\'][^>]*href=["\'])(?P<href>[^"\']*)(["\'][^>]*>)', re.IGNORECASE | re.DOTALL)

        def replace_link(match):
            lang = match.group('lang')
            old_href = match.group('href')
            target_href = pages[lang]
            
            if old_href != target_href:
                print(f"  [+] TROVATO {lang}: cambio {old_href} -> {target_href}")
                return f"{match.group(1)}{target_href}{match.group(4)}"
            return match.group(0)

        new_content, count = pattern.subn(replace_link, content)

        if count > 0 and new_content != content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f" [OK] {filename} aggiornato ({count} link modificati)")
        else:
            if "data-lang" not in content:
                print(f" [!] ATTENZIONE: La stringa 'data-lang' non esiste in {filename}!")
            else:
                print(f" [-] Nessuna modifica necessaria per {filename} (link già corretti o non trovati)")

    print("--- Fine ---")

if __name__ == "__main__":
    fix_sancarlo_ultra()