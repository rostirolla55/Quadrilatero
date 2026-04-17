import re
import sys
import os
from docx import Document
from googletrans import Translator

def process_document(input_file):
    if not os.path.exists(input_file):
        print(f"Errore: Il file {input_file} non esiste.")
        return

    # Lista delle lingue target
    languages = ['en', 'es', 'fr']
    
    translator = Translator()

    for lang in languages:
        doc = Document(input_file)
        img_mapping = {}
        img_counter = 1
        
        # Genera il nome file corretto: paginaID-it.docx -> paginaID-en.docx
        output_file = input_file.replace("-it.docx", f"-{lang}.docx")
        if output_file == input_file:
            output_file = f"traduzione_{lang}_{input_file}"

        print(f"Traduzione in corso: [{lang}]...")

        for paragraph in doc.paragraphs:
            if not paragraph.text.strip():
                continue

            # 1. Identificazione Tag
            pattern = r"\[SPLIT_BLOCK:(.*?)\]"
            matches = re.findall(pattern, paragraph.text)
            local_replacements = {}
            
            for original_name in matches:
                if img_counter <= 5:
                    placeholder = f"IMG_ID_{img_counter:03d}"
                    img_mapping[placeholder] = original_name
                    local_replacements[f"[SPLIT_BLOCK:{original_name}]"] = f"[SPLIT_BLOCK:{placeholder}]"
                    img_counter += 1

            # 2. Traduzione mantenendo formattazione
            for run in paragraph.runs:
                if not run.text.strip() or run.text.strip() in local_replacements.values(): 
                    continue
                
                text_to_translate = run.text
                for old_tag, new_placeholder in local_replacements.items():
                    text_to_translate = text_to_translate.replace(old_tag, new_placeholder)

                try:
                    translated_text = translator.translate(text_to_translate, src='it', dest=lang).text
                    
                    # 3. Ripristino e Pulizia
                    for placeholder, original_name in img_mapping.items():
                        if placeholder in translated_text:
                            translated_text = translated_text.replace(placeholder, original_name)
                    
                    # Pulizia spazi introdotti dal traduttore
                    translated_text = re.sub(r"\[\s*SPLIT_BLOCK\s*:\s*", "[SPLIT_BLOCK:", translated_text)
                    translated_text = re.sub(r"\s*\]", "]", translated_text)
                    
                    run.text = translated_text
                except Exception as e:
                    print(f"Errore run ({lang}): {e}")

        doc.save(output_file)
        print(f"Completato: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Trascina un file .docx sopra il file .bat")
    else:
        process_document(sys.argv[1])