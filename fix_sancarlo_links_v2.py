import os
from bs4 import BeautifulSoup

def fix_sancarlo_links_v2():
    # Mappa delle lingue e dei relativi file della Chiesa
    lang_map = {
        "it": "chiesasancarlo-it.html",
        "en": "chiesasancarlo-en.html",
        "es": "chiesasancarlo-es.html",
        "fr": "chiesasancarlo-fr.html"
    }

    print("Inizio riparazione link San Carlo (Versione 2)...")

    for current_lang, filename in lang_map.items():
        if not os.path.exists(filename):
            print(f" [!] File non trovato: {filename}")
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        modified = False
        # Cerchiamo i link nella sezione language-selector
        lang_selector = soup.find('div', class_='language-selector')
        
        if lang_selector:
            links = lang_selector.find_all('a')
            for a in links:
                target_lang = a.get('data-lang')
                if target_lang in lang_map:
                    new_href = lang_map[target_lang]
                    if a.get('href') != new_href:
                        print(f"  [{filename}] Cambio link {target_lang}: {a.get('href')} -> {new_href}")
                        a['href'] = new_href
                        modified = True

        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                # Usiamo prettify ma cerchiamo di mantenere la struttura
                f.write(soup.prettify(formatter="html"))
            print(f" [+] Salvato {filename}")
        else:
            print(f" [-] Nessuna modifica necessaria per {filename}")

if __name__ == "__main__":
    fix_sancarlo_links_v2()