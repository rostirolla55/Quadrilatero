import os
from bs4 import BeautifulSoup

def fix_sancarlo_smart():
    # Configurazione dei file corretti per ogni lingua
    pages = {
        "it": "chiesasancarlo-it.html",
        "en": "chiesasancarlo-en.html",
        "es": "chiesasancarlo-es.html",
        "fr": "chiesasancarlo-fr.html"
    }

    print("Inizio riparazione intelligente dei selettori lingua...")

    for current_lang, filename in pages.items():
        if not os.path.exists(filename):
            print(f" [!] Saltato {filename} (non trovato)")
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        modified = False
        # Cerchiamo il div language-selector
        selector = soup.find('div', class_='language-selector')
        
        if selector:
            # Troviamo tutti i link <a> al suo interno
            links = selector.find_all('a')
            for a in links:
                lang_attr = a.get('data-lang')
                if lang_attr in pages:
                    target_file = pages[lang_attr]
                    # Se il link attuale è diverso da quello che dovrebbe essere
                    if a.get('href') != target_file:
                        print(f"  [{filename}] Link {lang_attr}: {a.get('href')} -> {target_file}")
                        a['href'] = target_file
                        modified = True

        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                # Salviamo mantenendo la struttura originale il più possibile
                f.write(str(soup))
            print(f" [+] Salvato: {filename}")
        else:
            print(f" [-] Nessuna modifica necessaria per {filename}")

if __name__ == "__main__":
    fix_sancarlo_smart()