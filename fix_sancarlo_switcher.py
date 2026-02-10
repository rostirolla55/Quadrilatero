import os
from bs4 import BeautifulSoup

def fix_switcher():
    # Mappa dei file di San Carlo
    pages = {
        "it": "chiesasancarlo-it.html",
        "en": "chiesasancarlo-en.html",
        "es": "chiesasancarlo-es.html",
        "fr": "chiesasancarlo-fr.html"
    }

    for lang, filename in pages.items():
        if not os.path.exists(filename): continue
        
        with open(filename, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Cerchiamo i link che contengono le bandiere
        found = False
        for a in soup.find_all('a'):
            img = a.find('img')
            if img and 'flag' in img.get('src', '').lower():
                alt = img.get('alt', '').lower()
                # Se è la bandiera italiana, punta a chiesasancarlo-it.html
                if 'it' in alt or 'ital' in alt:
                    a['href'] = pages['it']
                    found = True
                elif 'en' in alt or 'engl' in alt:
                    a['href'] = pages['en']
                    found = True
                elif 'es' in alt or 'span' in alt or 'spag' in alt:
                    a['href'] = pages['es']
                    found = True
                elif 'fr' in alt or 'fren' in alt or 'fran' in alt:
                    a['href'] = pages['fr']
                    found = True

        if found:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(soup.prettify(formatter="html"))
            print(f"Corretti link lingua in {filename}")

if __name__ == "__main__":
    fix_switcher()