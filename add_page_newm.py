import sys
import os
import json
import datetime
import shutil
import re

# --- CONFIGURAZIONI GLOBALI ---
LANGUAGES = ['it', 'en', 'es', 'fr']
NAV_MARKER = '// ** MARKER: START NEW NAV LINKS **'
POI_MARKER = '// ** MARKER: START NEW POIS **'
HTML_NAV_MARKER = '</ul>'
HTML_TEMPLATE_NAME = 'template-it.html'
LANGUAGE_SWITCHER_MARKER = '<!-- LANGUAGE_SWITCHER_PLACEHOLDER -->'

LANGUAGE_NAMES = {'it': 'Italiano', 'en': 'English', 'es': 'Español', 'fr': 'Français'}

def get_translations_for_nav(page_title_it):
"""Genera traduzioni automatiche per il menu basate su parole chiave."""
mapping = {
"Basilica": {"en": "Basilica", "es": "Basílica", "fr": "Basilique"},
"Chiesa": {"en": "Church", "es": "Iglesia", "fr": "Église"},
"Santa": {"en": "Saint", "es": "San", "fr": "Saint"},
"Maria": {"en": "Mary", "es": "María", "fr": "Marie"},
"Maggiore": {"en": "Major", "es": "Mayor", "fr": "Majeure"}
}
translations = {'it': page_title_it}
for lang in ['en', 'es', 'fr']:
translated_title = page_title_it
for word_it, trans_dict in mapping.items():
if word_it.lower() in page_title_it.lower():
reg = re.compile(re.escape(word_it), re.IGNORECASE)
translated_title = reg.sub(trans_dict[lang], translated_title)
translations[lang] = translated_title
return translations

def update_main_js(repo_root, page_id, nav_key_id, lat, lon, distance):
js_path = os.path.join(repo_root, 'main.js')
new_poi = f"    {{ id: '{page_id}', lat: {lat}, lon: {lon}, distanceThreshold: {distance} }},"
new_nav = f"    {{ id: '{nav_key_id}', key: '{nav_key_id}', base: '{page_id}' }},"
try:
with open(js_path, 'r', encoding='utf-8') as f:
content = f.read()
if POI_MARKER in content and new_poi not in content:
content = content.replace(POI_MARKER, new_poi + '\n' + POI_MARKER)
if NAV_MARKER in content and new_nav not in content:
content = content.replace(NAV_MARKER, new_nav + '\n' + NAV_MARKER)
with open(js_path, 'w', encoding='utf-8') as f:
f.write(content)
print("main.js aggiornato.")
except Exception as e:
print(f"Errore main.js: {e}")


def update_texts_json(repo_root, page_id, nav_key_id, translations):
for lang in LANGUAGES:
json_path = os.path.join(repo_root, 'data', 'translations', lang, 'texts.json')
try:
with open(json_path, 'r', encoding='utf-8') as f:
data = json.load(f)
data['nav'][nav_key_id] = translations[lang]
if page_id not in data:
data[page_id] = {
"pageTitle": translations[lang],
"mainText": f"Contenuto per {translations[lang]}",
"audioSource": f"{lang}/{page_id}.mp3"
}
with open(json_path, 'w', encoding='utf-8') as f:
json.dump(data, f, indent=4, ensure_ascii=False)
print(f"JSON {lang} aggiornato.")
except Exception as e:
print(f"Errore JSON {lang}: {e}")


def generate_language_switcher(page_id, current_lang):
"""Genera i link per il cambio lingua da inserire nella nuova pagina."""
switcher_html = ['<ul class="language-switcher">']
for lang in LANGUAGES:
target_file = f'{page_id}-{lang}.html' if lang != 'it' else f'{page_id}.html'
is_active = ' active' if lang == current_lang else ''
switcher_html.append(f'        <li class="lang-item{is_active}"><a href="{target_file}" lang="{lang}">{LANGUAGE_NAMES[lang]}</a></li>')
switcher_html.append('    </ul>')
return '\n'.join(switcher_html)

def update_html_files(repo_root, page_id, nav_key_id, translations, page_title_it):
"""
1. Crea fisicamente i nuovi file HTML (it, en, es, fr).
2. Aggiorna il menu in tutti i file HTML della cartella.
"""
template_path = os.path.join(repo_root, HTML_TEMPLATE_NAME)
today_version = datetime.datetime.now().strftime("%Y%m%d_%H%M")

```
if not os.path.exists(template_path):
    print(f"ERRORE: Template {HTML_TEMPLATE_NAME} non trovato in {repo_root}")
    return

# --- 1. CREAZIONE NUOVI FILE ---
for lang in LANGUAGES:
    new_filename = f"{page_id}-{lang}.html" if lang != 'it' else f"{page_id}.html"
    new_path = os.path.join(repo_root, new_filename)
    
    if not os.path.exists(new_path):
        shutil.copyfile(template_path, new_path)
        with open(new_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Personalizza ID body e attributo lang
        content = content.replace('id="template"', f'id="{page_id}"')
        content = re.sub(r'<html lang="[a-z]{2}">', f'<html lang="{lang}">', content)
        
        # Inserisce lo switcher di lingua
        switcher = generate_language_switcher(page_id, lang)
        if LANGUAGE_SWITCHER_MARKER in content:
            content = content.replace(LANGUAGE_SWITCHER_MARKER, switcher)
        
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Creata nuova pagina: {new_filename}")

# --- 2. AGGIORNAMENTO MENU IN TUTTI I FILE ---
all_files = [f for f in os.listdir(repo_root) if f.endswith('.html') and f != HTML_TEMPLATE_NAME]

for filename in all_files:
    file_path = os.path.join(repo_root, filename)
    
    current_lang = 'it'
    for l in ['en', 'es', 'fr']:
        if f'-{l}.html' in filename: current_lang = l

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if f'id="{nav_key_id}"' not in content:
            target_href = f'{page_id}-{current_lang}.html' if current_lang != 'it' else f'{page_id}.html'
            label = translations.get(current_lang, page_title_it)
            
            # Inserimento link pulito senza doppie graffe
            nav_link = f'                <li><a id="{nav_key_id}" href="{target_href}">{label}</a></li>'
            
            if HTML_NAV_MARKER in content:
                parts = content.rsplit(HTML_NAV_MARKER, 1)
                content = parts[0] + nav_link + '\n            ' + HTML_NAV_MARKER + parts[1]
            
            # Cache busting
            content = re.sub(r'main\.js\?v=[0-9A-Z_]*', f'main.js?v={today_version}', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Menu aggiornato in {filename}")
    except Exception as e:
        print(f"Errore durante l'aggiornamento di {filename}: {e}")

```

def main():
if len(sys.argv) < 8:
print("Parametri insufficienti.")
return

```
page_id, nav_key_id, title, lat, lon, dist, root = sys.argv[1:8]

print(f"\nAVVIO AGGIORNAMENTO: {page_id}")
translations = get_translations_for_nav(title)

update_texts_json(root, page_id, nav_key_id, translations)
update_main_js(root, page_id, nav_key_id, lat, lon, dist)
update_html_files(root, page_id, nav_key_id, translations, title)

print(f"\nOperazione completata per {page_id}!")

```

if **name** == "**main**":
main()
