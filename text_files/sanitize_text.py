import sys
import os

def sanitize_for_json(input_filepath):
    """
    Legge un file, esegue l'escape dei doppi apici e rimuove gli a capo,
    stampando la stringa risultante.
    """
    if not os.path.exists(input_filepath):
        # Stampa solo l'errore sul flusso standard per non interrompere la redirezione se necessario
        print(f"ERRORE: File non trovato: {input_filepath}", file=sys.stderr) 
        return ""

    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Escape dei doppi apici
        sanitized_content = content.replace('"', '\\"')

        # 2. Eliminazione di tutti i caratteri di a capo per una singola riga
        sanitized_content = sanitized_content.replace('\r\n', ' ')
        sanitized_content = sanitized_content.replace('\n', ' ')
        
        # Eliminiamo eventuali spazi multipli consecutivi
        sanitized_content = " ".join(sanitized_content.split())
        
        return sanitized_content

    except Exception as e:
        print(f"Si è verificato un errore durante l'elaborazione del file: {e}", file=sys.stderr)
        return ""

if __name__ == "__main__":
    if len(sys.argv) != 2:
        # Se i parametri non sono corretti, stampa l'uso su stderr
        print("Uso: python sanitize_text.py <percorso_del_file_html>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    result = sanitize_for_json(input_file)
    
    # Stampa solo il risultato finale su stdout
    print(result)