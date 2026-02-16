import os
import glob

def cleanup_after_dimissione(page_id, languages=['it', 'en', 'fr', 'es']):
    """
    Esegue la pulizia dei file obsoleti dopo il processo di dimissione.
    Rimuove file audio .mp3 e frammenti .html (maintext).
    """
    print(f"--- Inizio pulizia per la pagina: {page_id} ---")
    
    # Percorso base per gli audio (Assets/Audio/it/chiesasancarlo.mp3)
    audio_base_path = os.path.join("Assets", "Audio")
    
    # Contatore file rimossi
    removed_count = 0

    for lang in languages:
        # 1. Rimozione Audio
        audio_path = os.path.join(audio_base_path, lang, f"{page_id}.mp3")
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                print(f"[AUDIO] Rimosso: {audio_path}")
                removed_count += 1
            except Exception as e:
                print(f"[ERRORE] Impossibile rimuovere audio {audio_path}: {e}")

        # 2. Rimozione Frammenti HTML (it_chiesasancarlo_maintext*.html)
        # Usiamo glob per trovare tutti i frammenti numerati (maintext1, maintext2, ecc.)
        fragment_pattern = f"{lang}_{page_id}_maintext*.html"
        fragments = glob.glob(fragment_pattern)
        
        for fragment in fragments:
            try:
                os.remove(fragment)
                print(f"[FRAMMENTO] Rimosso: {fragment}")
                removed_count += 1
            except Exception as e:
                print(f"[ERRORE] Impossibile rimuovere frammento {fragment}: {e}")

    if removed_count == 0:
        print("Nessun file obsoleto trovato (audio o frammenti).")
    else:
        print(f"Pulizia terminata. Totale file eliminati: {removed_count}")

if __name__ == "__main__":
    # Esempio: python cleanup_fragments.py chiesasancarlo
    import sys
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
        cleanup_after_dimissione(target)
    else:
        # Se non passato come argomento, puoi testarlo qui
        # target_page = "chiesasancarlo"
        # cleanup_after_dimissione(target_page)
        print("Errore: specifica l'ID della pagina (es: python cleanup_fragments.py chiesasancarlo)")