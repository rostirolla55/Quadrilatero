import os

def collect_all_code():
    # File di output
    output_filename = "full_code.txt"
    # Estensioni da includere nella scansione
    valid_extensions = ('.py', '.bat', '.js', '.html', '.css', '.json')
    # Cartelle da escludere (opzionale, ad esempio cartelle virtual environment)
    exclude_dirs = {'.git', '__pycache__', 'venv', 'node_modules'}
    
    count = 0

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write("="*50 + "\n")
        outfile.write("FULL PROJECT CODE EXPORT\n")
        outfile.write("="*50 + "\n\n")

        for root, dirs, files in os.walk('.'):
            # Esclude le cartelle non necessarie
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith(valid_extensions) and file != output_filename:
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            
                            # Scrive l'intestazione del file
                            outfile.write(f"\n\n{'#'*80}\n")
                            outfile.write(f"FILE: {file_path}\n")
                            outfile.write(f"{'#'*80}\n\n")
                            
                            # Scrive il contenuto
                            outfile.write(content)
                            outfile.write("\n")
                            
                            print(f"Incluso: {file_path}")
                            count += 1
                    except Exception as e:
                        print(f"Errore nella lettura di {file_path}: {e}")

    print(f"\nOperazione completata! Creato '{output_filename}' con {count} file.")

if __name__ == "__main__":
    collect_all_code()