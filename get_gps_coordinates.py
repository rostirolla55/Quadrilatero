import re

def get_gps_coordinates():
    print("\n--- Configurazione GPS ---")
    print("Vai su Google Maps, clicca col tasto destro sul punto e copia le coordinate.")
    coords_input = input("Incolla qui le coordinate (es. 44.4949, 11.3426): ")
    
    # Pulizia input: estrae coppie di numeri decimali
    match = re.findall(r"[-+]?\d*\.\d+|\d+", coords_input)
    if len(match) >= 2:
        lat, lon = match[0], match[1]
        print(f"✅ Coordinate acquisite: Lat {lat}, Lon {lon}")
        return lat, lon
    else:
        print("❌ Formato non valido. Riprova.")
        return get_gps_coordinates()