import json
import os
import re
from docx import Document
from gtts import gTTS # Libreria gratuita e immediata

def clean_coordinates(input_str):
    coords = re.findall(r"[-+]?\d*\.\d+|\d+", input_str)
    if len(coords) >= 2:
        return {"lat": coords[0], "lng": coords[1]}
    return None

def get_text_from_docx(poi_id):
    path = f"DOCS_DA_CONVERTIRE/{poi_id}.docx"
    if not os.path.exists(path):
        print(f"⚠️ File {path} non trovato!")
        return None
    doc = Document(path)
    # Filtriamo via i tag come [TITOLO] per la lettura audio
    testo = []
    for p in doc.paragraphs:
        line = p.text.strip()
        if line and not line.startswith("["):
            testo.append(line)
    return " ".join(testo)

def generate_audio_free(text, output_path):
    print(f"🎙 Generazione audio MP3 in corso (gTTS)...")
    try:
        tts = gTTS(text=text, lang='it')
        tts.save(output_path)
        print(f"✅ Audio creato con successo: {output_path}")
    except Exception as e:
        print(f"❌ Errore generazione audio: {e}")

def run():
    poi_id = "stabile_legno_vandini"
    print(f"=== Automazione POI: {poi_id} ===")
    
    # 1. Coordinate
    gps_input = input("Incolla le coordinate di Via del Porto 11: ")
    coords = clean_coordinates(gps_input)
    if not coords: return

    # 2. Testo
    testo_per_audio = get_text_from_docx(poi_id)
    if not testo_per_audio: return

    # 3. Cartelle e Audio
    audio_dir = f"public/audio/{poi_id}"
    os.makedirs(audio_dir, exist_ok=True)
    generate_audio_free(testo_per_audio, f"{audio_dir}/it.mp3")

    # 4. JSON
    config_file = 'pois_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except: data = {}
    else: data = {}

    data[poi_id] = {
        "id": poi_id,
        "coords": [float(coords['lat']), float(coords['lng'])],
        "image": f"/images/{poi_id}.jpg",
        "audio": {"it": f"/audio/{poi_id}/it.mp3"}
    }

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\n🚀 Pagina '{poi_id}' COMPLETATA!")
    print(f"📁 Audio salvato in {audio_dir}/it.mp3")
    print(f"📍 Configurazione JSON aggiornata.")

if __name__ == "__main__":
    run()