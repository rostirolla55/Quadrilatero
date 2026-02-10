import os
from bs4 import BeautifulSoup

def fix_sancarlo_navigation():
    # Definiamo i file della Chiesa di San Carlo
    sancarlo_files = {
        "it": "chiesasancarlo-it.html",
        "en": "chiesasancarlo-en.html",
        "es": "chiesasancarlo-es.html",
        "fr": "chiesasancarlo-fr.html"
    }

    print("Inizio riparazione link lingue per San Carlo...")

    for lang, filename in sancarlo_files.items():
        if not os.path.exists(filename):
            print(f" [!] File non trovato: {filename}")
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Cerchiamo i link che gestiscono il cambio lingua
        # Solitamente sono <a> con un <img> dentro (la bandiera)
        links = soup.find_all('a')
        modified = False

        for a in links:
            img = a.find('img')
            if img:
                alt_text = img.get('alt', '').lower()
                src_text = img.get('src', '').lower()
                
                # Identifichiamo la lingua di destinazione della bandiera
                target_lang = None
                if 'it' in alt_text or 'ital' in src_text: target_lang = 'it'
                elif 'en' in alt_text or 'engl' in src_text or 'uk' in src_text: target_lang = 'en'
                elif 'es' in alt_text or 'span' in src_text or 'spag' in src_text: target_lang = 'es'
                elif 'fr' in alt_text or 'fren' in src_text or 'fran' in src_text: target_lang = 'fr'

                if target_lang:
                    # Impostiamo il link corretto verso il file della lingua target
                    correct_href = sancarlo_files[target_lang]
                    if a.get('href') != correct_href:
                        print(f"  [{filename}] Correzione bandiera {target_lang}: {a.get('href')} -> {correct_href}")
                        a['href'] = correct_href
                        modified = True

        if modified:
            with open(filename, 'w', encoding='utf-8') as f:
                # Scriviamo il file formattato correttamente
                f.write(soup.prettify(formatter="html"))
            print(f" [+] Salvato {filename}")
        else:
            print(f" [-] Nessuna modifica necessaria per {filename}")

if __name__ == "__main__":
    fix_sancarlo_navigation()