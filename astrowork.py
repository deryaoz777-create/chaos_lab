import swisseph as swe

# Tarih ve saat
from datetime import datetime, timezone

# Şu anki zaman (UTC)
simdi = datetime.now(timezone.utc)
yil = simdi.year
ay = simdi.month
gun = simdi.day
saat = simdi.hour + simdi.minute/60 + simdi.second/3600

jd = swe.julday(yil, ay, gun, saat)

# Julian Day
jd = swe.julday(yil, ay, gun, saat)

# Konum (Kutaisi, Gürcistan)
enlem = 42.2679
boylam = 42.7181

# Evler - Regiomontanus
evler, asc_bilgi = swe.houses(jd, enlem, boylam, b'R')

for i, derece in enumerate(evler):
    print(f"{i+1}. Ev: {derece:.2f}°")

print(f"\nAsendant: {asc_bilgi[0]:.2f}°")

# Gezegenler
gezegenler = {
    "Güneş": swe.SUN,
    "Ay": swe.MOON,
    "Merkür": swe.MERCURY,
    "Venüs": swe.VENUS,
    "Mars": swe.MARS,
    "Jüpiter": swe.JUPITER,
    "Satürn": swe.SATURN,
}

print("\n--- Gezegenler ---")
for isim, kod in gezegenler.items():
    pozisyon, _ = swe.calc_ut(jd, kod)
    print(f"{isim}: {pozisyon[0]:.2f}°")
def derece_to_burc(derece):
    burclar = [
        "Koç", "Boğa", "İkizler", "Yengeç", 
        "Aslan", "Başak", "Terazi", "Akrep", 
        "Yay", "Oğlak", "Kova", "Balık"
    ]
    index = int(derece / 30)
    burc_derece = derece % 30
    return f"{burclar[index]} {burc_derece:.2f}°"

print("\n--- Gezegenler ---")
for isim, kod in gezegenler.items():
    pozisyon, _ = swe.calc_ut(jd, kod)
    burc = derece_to_burc(pozisyon[0])
    print(f"{isim}: {burc}")

print(f"\nAsendant: {derece_to_burc(asc_bilgi[0])}")

print("\n--- Evler ---")
for i, derece in enumerate(evler):
    print(f"{i+1}. Ev: {derece_to_burc(derece)}")
    def gezegen_hangi_ev(gezegen_derece, evler):
        for i in range(12):
            ev_baslangic = evler[i]
            ev_bitis = evler[(i + 1) % 12]
        
        if ev_baslangic > ev_bitis:
            if gezegen_derece >= ev_baslangic or gezegen_derece < ev_bitis:
                return i + 1
        else:
            if ev_baslangic <= gezegen_derece < ev_bitis:
                return i + 1
        return 1    
