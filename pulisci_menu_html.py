import os
import re

# Struttura pulita da iniettare
NUOVO_NAV_HTML = '''<nav class="nav-bar-main" id="navBarMain">
    <div class="nav-bar-content">
      <!-- Popolato automaticamente da main.js -->
    </div>
   </nav>'''

def pulisci_menu_in_file(filepath):
    """
    Legge un file HTML e sostituisce il vecchio blocco <nav id="navBarMain">
    con la versione alleggerita.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contenuto = f.read()

        # Regex per intercettare l'intero tag <nav ... id="navBarMain">...</nav>
        # (gestisce eventuali spazi, a capo o elenchi <ul>/<li> interni)
        pattern = r'<nav\b[^>]*id=["\']navBarMain["\'][^>]*>[\s\S]*?</nav>'

        if re.search(pattern, contenuto, flags=re.IGNORECASE):
            contenuto_modificato = re.sub(pattern, NUOVO_NAV_HTML, contenuto, flags=re.IGNORECASE)

            # Sovrascrive il file solo se c'è stata un'effettiva modifica
            if contenuto != contenuto_modificato:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(contenuto_modificato)
                print(f"[OK] Pulito: {os.path.basename(filepath)}")
                return True
            else:
                print(f"[SKIP] Già pulito: {os.path.basename(filepath)}")
                return False
        else:
            print(f"[INFO] Nessun menu navBarMain trovato in: {os.path.basename(filepath)}")
            return False

    except Exception as e:
        print(f"[ERRORE] Impossibile elaborare {os.path.basename(filepath)}: {e}")
        return False

def elabora_directory(root_dir):
    """
    Scansiona la cartella principale ed elabora tutti i file .html
    """
    print(f"=== Avvio Pulizia Menu HTML nella cartella: {root_dir} ===\n")
    maggiorazione_conteggio = 0

    for file in os.listdir(root_dir):
        if file.endswith('.html'):
            filepath = os.path.join(root_dir, file)
            if pulisci_menu_in_file(filepath):
                maggiorazione_conteggio += 1

    print(f"\n=== Operazione completata! File modificati: {maggiorazione_conteggio} ===")

if __name__ == "__main__":
    # Rileva la cartella corrente in cui si trova lo script
    cartella_lavoro = os.path.dirname(os.path.abspath(__file__))
    elabora_directory(cartella_lavoro)