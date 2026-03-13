"""
server.py — Horary Flask Backend
Kurulum: pip install flask
Çalıştır: python server.py
"""

from flask import Flask, request, jsonify, send_from_directory
import datetime
import os
from horary_engine import (
    calc_chart, chart_to_dict, build_frawley_prompt,
    ask_claude, detect_question_type, get_house_ruler,
    PLANET_TR, SIGN_NAMES_TR, ESSENTIAL_DIGNITY_TABLE
)

app = Flask(__name__, static_folder=".")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
print(f"[STARTUP] ANTHROPIC_API_KEY {'tanımlı (' + ANTHROPIC_API_KEY[:10] + '...)' if ANTHROPIC_API_KEY else 'TANIMLI DEĞİL'}")

# Günlük vibe cache — her burç için bir kez üretilir, gün boyunca saklanır
_daily_cache = {}  # { "YYYY-MM-DD:BurçAdı": {text, mood, energy} }

# Koordinatlar — Terjola default, kullanıcı değiştirebilir
DEFAULT_LAT = 42.17
DEFAULT_LON = 42.67


@app.route("/")
def index():
    return send_from_directory(".", "yildizlar-biliyor.html")


@app.route("/api/chart", methods=["POST"])
def api_chart():
    """
    Harita hesapla + Claude yorumu al.
    Body: { question, lat, lon, datetime, api_key }
    """
    data = request.json or {}

    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Soru boş olamaz"}), 400

    lat = float(data.get("lat", DEFAULT_LAT))
    lon = float(data.get("lon", DEFAULT_LON))
    api_key = data.get("api_key") or ANTHROPIC_API_KEY

    # Tarih/saat
    dt_str = data.get("datetime")
    if dt_str:
        try:
            dt = datetime.datetime.fromisoformat(dt_str)
        except:
            dt = datetime.datetime.now()
    else:
        dt = datetime.datetime.now()

    try:
        chart = calc_chart(question, dt, lat, lon)
        chart_data = chart_to_dict(chart)
        prompt = build_frawley_prompt(chart)

        # Soru tipi
        q_type = detect_question_type(question)

        # Significatörler
        lord1 = get_house_ruler(chart, 1)
        lord1_planet = chart.planets.get(lord1)

        # Claude yorumu
        interpretation = None
        if api_key:
            print(f"[API] Yorum isteniyor, key: {api_key[:10]}...")
            interpretation = ask_claude(prompt, api_key)
            print(f"[API] Sonuç: {interpretation[:100] if interpretation else 'BOŞ'}...")
        else:
            print("[API] API key yok, yorum atlanıyor")

        # Günlük vibe (Ay burcuna göre)
        moon = chart_data["planets"]["moon"]
        vibe = get_moon_vibe(moon["sign"], chart_data["is_daytime"])

        return jsonify({
            "success": True,
            "chart": chart_data,
            "interpretation": interpretation,
            "question_type": q_type["desc"],
            "lord1": PLANET_TR.get(lord1, lord1),
            "moon_sign": moon["sign"],
            "vibe": vibe,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/vibe", methods=["POST"])
def api_vibe():
    """Günlük vibe — cache varsa cache'den, yoksa Claude'dan üret."""
    data = request.json or {}
    sign = data.get("sign", "Koç")
    today = datetime.date.today().isoformat()
    cache_key = f"{today}:{sign}"

    # Cache'de varsa direkt dön
    if cache_key in _daily_cache:
        return jsonify(_daily_cache[cache_key])

    # Claude ile üret
    if ANTHROPIC_API_KEY:
        try:
            vibe = generate_daily_vibe(sign, ANTHROPIC_API_KEY)
            _daily_cache[cache_key] = vibe
            return jsonify(vibe)
        except Exception as e:
            pass  # Hata olursa fallback'e düş

    # Fallback — statik vibe
    return jsonify(get_moon_vibe(sign, True))


@app.route("/api/daily-preload", methods=["POST"])
def api_daily_preload():
    """Tüm 12 burç için günlük vibe'ı önceden üret ve cache'le."""
    if not ANTHROPIC_API_KEY:
        return jsonify({"error": "API key yok"}), 400
    
    signs = ["Koç","Boğa","İkizler","Yengeç","Aslan","Başak",
             "Terazi","Akrep","Yay","Oğlak","Kova","Balık"]
    today = datetime.date.today().isoformat()
    results = {}
    
    for sign in signs:
        cache_key = f"{today}:{sign}"
        if cache_key not in _daily_cache:
            try:
                vibe = generate_daily_vibe(sign, ANTHROPIC_API_KEY)
                _daily_cache[cache_key] = vibe
                results[sign] = "üretildi"
            except:
                results[sign] = "hata"
        else:
            results[sign] = "cache'de vardı"
    
    return jsonify({"success": True, "results": results})


def generate_daily_vibe(sign: str, api_key: str) -> dict:
    """
    O günün gerçek gökyüzünü kullanarak Claude'a burç için günlük vibe ürettir.
    Sonuç: {text, mood, energy}
    """
    from horary_engine import calc_chart, SIGN_NAMES_TR, PLANET_TR
    import json as _json

    # Bugünün haritasını hesapla (öğlen, sabit konum)
    now = datetime.datetime.now().replace(hour=12, minute=0)
    chart = calc_chart("Günlük enerji", now, 42.17, 42.67)

    # Gezegen özetini çıkar
    planet_lines = []
    for pname, planet in chart.planets.items():
        retro = " ℞" if planet.retrograde else ""
        planet_lines.append(
            f"{PLANET_TR[pname]}: {int(planet.sign_degree)}° {SIGN_NAMES_TR[planet.sign_index]}{retro} (Ev {planet.house})"
        )
    planet_summary = "\n".join(planet_lines)

    prompt = f"""Bugünün gökyüzü:
{planet_summary}

Burç: {sign}
Tarih: {now.strftime("%d %B %Y")}

Bu gezegen pozisyonlarına dayanarak {sign} burcu için bugünün enerjisini yaz.

KURALLAR:
- İğneleyici, esprili, "zaten biliyordun" tonu — aşırı pozitif değil
- Türkçe yaz
- 2-3 cümle, max 60 kelime
- Mood badge: 2-4 kelime, büyük harf, o günün havasını özetleyen (örn: "YANGIN MOD", "SİS İÇİNDE")
- 4 enerji barı: her biri 0-100 arası, {sign} için anlamlı etiketler

Sadece JSON döndür, başka hiçbir şey yazma:
{{"text": "...", "mood": "...", "energy": {{"Etiket1": 80, "Etiket2": 45, "Etiket3": 70, "Etiket4": 30}}}}"""

    response = ask_claude(prompt, api_key)
    
    # JSON parse
    try:
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        result = _json.loads(clean.strip())
        # Gerekli alanlar var mı kontrol et
        if "text" in result and "mood" in result and "energy" in result:
            return result
    except:
        pass
    
    # Parse başarısızsa fallback
    return get_moon_vibe(sign, True)


def get_moon_vibe(sign: str, is_daytime: bool) -> dict:
    """Ay burcuna göre günlük enerji."""
    VIBES = {
        "Koç":     {"text": "Mars bugün aceleciliğinizi körüklüyor. Evet, herkese önce girmek istiyorsunuz — ama trafik ışığı herkese aynı anda kırmızı yanar. Bir soluk alın.", "mood": "YANGIN MOD", "energy": {"Enerji": 90, "Sabır": 12, "Ego": 95, "Sezgi": 40}},
        "Boğa":    {"text": "Venüs size konfor vaat ediyor ama Satürn faturayı gönderiyor. Güzel şeyler istiyorsunuz, para mı var? Varsa harcayın — yoksa da yine harcarsınız zaten.", "mood": "KONFOR KOMA", "energy": {"Enerji": 45, "İnat": 99, "Keyif": 80, "Değişim": 5}},
        "İkizler": {"text": "Merkür beş farklı fikri aynı anda düşünmenizi sağlıyor. Bunların hepsini birden söyleyeceksiniz ve hiçbirini bitirmeyeceksiniz. Klasik.", "mood": "KAOTİK ZİHİN", "energy": {"Enerji": 85, "Odak": 15, "Merak": 98, "Sonuç": 20}},
        "Yengeç":  {"text": "Ay bugün duygusal tüm kapıları açık bıraktı. Birileri sizi üzerse ağlarsınız, mutlu ederse de ağlarsınız. Mendil hazır olsun.", "mood": "DUYGU OKYANUSU", "energy": {"Empati": 99, "Mesafe": 5, "Koruma": 85, "Bırakma": 10}},
        "Aslan":   {"text": "Güneş doğrudan üzerinize parlıyor ve siz bunu hak ettiğinizi düşünüyorsunuz. Belki de öyle. Ama bugün herkes kendi Güneş'inin altında.", "mood": "SAHNE BENİM", "energy": {"Özgüven": 99, "Alçakgönüllülük": 8, "Karizma": 95, "Dinleme": 20}},
        "Başak":   {"text": "Merkür her hatayı gösteriyor — başkalarının ve özellikle kendinizin. Eleştiri yeteneğiniz zirvedeyken eleştirilmekten nefret etmeniz ilginç bir paradoks.", "mood": "ANALİZ SIKIŞMASI", "energy": {"Dikkat": 99, "Öz-merhamet": 15, "Verimlilik": 85, "Mükemmelcilik": 100}},
        "Terazi":  {"text": "Venüs denge istiyor ama siz bugün karardan kaçıyorsunuz. Öğle yemeği seçmek bile varoluşsal bir kriz gibi geliyor. Bu bir burç özelliği, tedavisi yok.", "mood": "KARARSIZLIK DÖNEMİ", "energy": {"Uyum": 90, "Karar": 18, "Estetik": 95, "Net Tavır": 10}},
        "Akrep":   {"text": "Mars ve Plüton bugün sizi daha da yoğunlaştırıyor. Birisi sizi 'fazla ciddi' bulacak. Onlara aldırmayın — siz zaten her şeyi biliyorsunuz, onlar fark etmedi.", "mood": "DERİN SULAR", "energy": {"Yoğunluk": 100, "Güven": 30, "Sezgi": 98, "Hafiflik": 5}},
        "Yay":     {"text": "Jüpiter bugün sizi biraz fazla iyimser yapıyor. Hayır, o proje bir haftada bitmez. Hayır, o para yarın gelmez. Ama evet, enerjiniz harika.", "mood": "OPTİMİZM AŞIMI", "energy": {"Coşku": 98, "Gerçekçilik": 20, "Özgürlük": 90, "Taahhüt": 15}},
        "Oğlak":   {"text": "Satürn her zamanki gibi sorumluluğunuzu hatırlatıyor. Tatil planlarken bile 'ama şu iş nasıl olacak' diye düşünüyorsunuz. Bugün biraz bırakın. Olmayacak ama söylemek gerekti.", "mood": "SORUMLULUK TİRANI", "energy": {"Disiplin": 99, "Eğlence": 25, "Sabır": 90, "Spontanlık": 8}},
        "Kova":    {"text": "Satürn yapıyı, Uranüs devrimi temsil ediyor — ikiniz de sizin içinizde savaşıyor. Hem sistemi değiştirmek hem de sisteme ait olmak istiyorsunuz. Bu çelişki sizi yoracak.", "mood": "DEVRİMCİ KAFA", "energy": {"Özgünlük": 95, "Bağlılık": 20, "Vizyon": 90, "Pratiklik": 25}},
        "Balık":   {"text": "Neptün bugün gerçekle hayali birbirine karıştırıyor. Güzel bir his ama toplantınız öğleden sonra. Ve evet, gerçek bir toplantı.", "mood": "SİS İÇİNDE", "energy": {"Sezgi": 98, "Sınır": 8, "Yaratıcılık": 95, "Zamanlama": 15}},
    }
    return VIBES.get(sign, VIBES["Koç"])


if __name__ == "__main__":
    print("=" * 50)
    print("🔮 Horary Server başlıyor...")
    print("📍 http://localhost:5000")
    print("=" * 50)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
