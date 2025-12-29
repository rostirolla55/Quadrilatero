def update_navigation_menu(repo_root, nav_key_id, page_id, page_title_it):
    """
    Aggiorna il menu di navigazione in tutti i file HTML, 
    incluso esplicitamente il file template.html.
    """
    import os

    # 1. Definiamo la riga da inserire (usando l'ID per il multilingua gestito da main.js)
    # Esempio: <li><a id="navNuovaPagina" href="nuovapagina-it.html">Titolo</a></li>
    new_nav_item = f'                    <li><a id="{nav_key_id}" href="{page_id}-it.html">{page_title_it}</a></li>'

    # 2. Lista dei file da elaborare: tutti i file .html nella root + template.html
    html_files = [f for f in os.listdir(repo_root) if f.endswith('.html')]
    
    # Se il template è in una sottocartella o ha un nome specifico, assicuriamoci di includerlo
    if 'template.html' not in html_files and os.path.exists(os.path.join(repo_root, 'template.html')):
        html_files.append('template.html')

    for filename in html_files:
        file_path = os.path.join(repo_root, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verifica se la voce è già presente per evitare duplicati
        if f'id="{nav_key_id}"' in content:
            print(f"  - Nota: {nav_key_id} già presente in {filename}. Salto.")
            continue

        # Inserimento dinamico prima della chiusura della lista </ul>
        if '</ul>' in content:
            # Sostituiamo l'ultima occorrenza di </ul> per sicurezza
            updated_content = content.replace('</ul>', f'    {new_nav_item}\n                </ul>', 1)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"  ✅ Menu aggiornato in: {filename}")
        else:
            print(f"  ⚠️ Attenzione: Tag </ul> non trovato in {filename}")