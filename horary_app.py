from __future__ import annotations

import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import swisseph as swe

from astro_calc import (
    Location,
    aspect,
    deg_to_sign_tr,
    fmt_sign_deg_tr,
    house_of_degree,
    houses_regiomontanus,
    julian_day,
    now_utc,
    planet_positions,
)


PLANETS: Dict[str, int] = {
    "Güneş": swe.SUN,
    "Ay": swe.MOON,
    "Merkür": swe.MERCURY,
    "Venüs": swe.VENUS,
    "Mars": swe.MARS,
    "Jüpiter": swe.JUPITER,
    "Satürn": swe.SATURN,
}


SIGN_RULER_TR = {
    "Koç": "Mars",
    "Boğa": "Venüs",
    "İkizler": "Merkür",
    "Yengeç": "Ay",
    "Aslan": "Güneş",
    "Başak": "Merkür",
    "Terazi": "Venüs",
    "Akrep": "Mars",
    "Yay": "Jüpiter",
    "Oğlak": "Satürn",
    "Kova": "Satürn",
    "Balık": "Jüpiter",
}

SIGN_ELEMENT = {
    "Koç": "ateş",
    "Aslan": "ateş",
    "Yay": "ateş",
    "Boğa": "toprak",
    "Başak": "toprak",
    "Oğlak": "toprak",
    "İkizler": "hava",
    "Terazi": "hava",
    "Kova": "hava",
    "Yengeç": "su",
    "Akrep": "su",
    "Balık": "su",
}


PRESETS: Dict[str, Location] = {
    "1": Location("İstanbul", 41.0082, 28.9784),
    "2": Location("Ankara", 39.9334, 32.8597),
    "3": Location("İzmir", 38.4237, 27.1428),
    "4": Location("Kutaisi", 42.2679, 42.7181),
    "5": Location("Tbilisi", 41.7151, 44.8271),
}


@dataclass(frozen=True)
class HorarySnapshot:
    dt_utc: datetime
    location: Location
    jd: float
    cusps: List[float]
    asc: float
    planets_lon: Dict[str, float]


def build_snapshot(dt_utc: datetime, loc: Location) -> HorarySnapshot:
    jd = julian_day(dt_utc)
    cusps, asc = houses_regiomontanus(jd, loc)
    planets = planet_positions(jd, PLANETS)
    planets_lon = {p.name: p.lon for p in planets}
    return HorarySnapshot(dt_utc=dt_utc, location=loc, jd=jd, cusps=cusps, asc=asc, planets_lon=planets_lon)


def radicality_flags(asc_deg: float, saturn_deg: float) -> List[str]:
    sign, within = deg_to_sign_tr(asc_deg)
    flags: List[str] = []
    if within < 3.0:
        flags.append("Yükselen çok erken derecede: soru daha ‘tam pişmemiş’ olabilir.")
    if within > 27.0:
        flags.append("Yükselen çok geç derecede: süreç ‘kapanış’ modunda olabilir.")
    if sign in ("Koç", "Boğa", "İkizler", "Yengeç"):
        # playful horary-ish warning, not a rule
        pass
    # classic-ish warning: Saturn in 7th (roughly)
    # We don't have a full house for Saturn without cusps here; caller can add.
    _ = saturn_deg
    return flags


def vibe_text(snapshot: HorarySnapshot) -> str:
    asc_sign, asc_within = deg_to_sign_tr(snapshot.asc)
    moon_lon = snapshot.planets_lon["Ay"]
    moon_sign, moon_within = deg_to_sign_tr(moon_lon)

    asc_elem = SIGN_ELEMENT[asc_sign]
    moon_elem = SIGN_ELEMENT[moon_sign]
    ruler = SIGN_RULER_TR[asc_sign]

    moon_house = house_of_degree(moon_lon, snapshot.cusps)
    sat_house = house_of_degree(snapshot.planets_lon["Satürn"], snapshot.cusps)

    flags = radicality_flags(snapshot.asc, snapshot.planets_lon["Satürn"])
    if sat_house == 7:
        flags.append("Satürn 7. evde: konu ‘ciddiyet/çekince/bedel’ tonunu artırabilir (eğlence amaçlı uyarı).")

    # simple aspect between Moon and ASC ruler
    # Not: Eğer yükselen yöneticisi zaten Ay ise, “Ay ile Ay kavuşumu” gibi
    # anlamsız bir ifade üretmemek için açı hesabını atlıyoruz.
    ruler_lon = snapshot.planets_lon.get(ruler)
    if ruler == "Ay" or ruler_lon is None:
        asp_txt = "Bu haritada Ay zaten yükselen yöneticisi: tek bir ana hikâye ekseni var."
    else:
        asp = aspect(moon_lon, ruler_lon, orb=6.0)
        if asp:
            name, delta = asp
            asp_txt = f"Ay ile {ruler} arasında {name} var (yaklaşık {delta:.1f}°): hikâye daha ‘bağlanıyor’."
        else:
            asp_txt = "Ay, yükselen yöneticisiyle net bir bağ kurmuyor: akış dolaylı/karmaşık olabilir."

    mood_lines: List[str] = []
    mood_lines.append(f"Yükselen: {fmt_sign_deg_tr(snapshot.asc)} ({asc_elem}).")
    mood_lines.append(f"Ay: {fmt_sign_deg_tr(moon_lon)} (ev {moon_house}, {moon_elem}).")
    mood_lines.append(f"Yükselen yöneticisi: {ruler}.")
    mood_lines.append(asp_txt)

    # vibe synthesis (playful)
    if asc_elem == "ateş" and moon_elem == "ateş":
        vibe = "Hızlı karar, hızlı aksiyon; ‘deneyip görelim’ modu."
    elif asc_elem == "toprak" and moon_elem == "toprak":
        vibe = "Gerçekçilik ve somut plan; küçük ama sağlam adım."
    elif asc_elem == "hava" and moon_elem == "hava":
        vibe = "Zihin hızlanıyor: konuşma, yazışma, seçenekleri tartma."
    elif asc_elem == "su" and moon_elem == "su":
        vibe = "Sezgi yüksek: hisler, rüyalar, alt metinler daha baskın."
    else:
        vibe = "Denge arayışı: biri gaza basarken diğeri ‘bir dur’ diyor."

    mood_lines.append("")
    mood_lines.append(f"Anın ruhu: {vibe}")
    mood_lines.append(f"Alt ton: Yükselen {asc_sign} ({asc_within:.1f}°) ‘nasıl’ı; Ay {moon_sign} ({moon_within:.1f}°) ‘neden’i anlatıyor.")
    if flags:
        mood_lines.append("")
        mood_lines.append("Notlar:")
        mood_lines.extend([f"- {x}" for x in flags])

    return "\n".join(mood_lines)


def prompt_location() -> Location:
    print("Konum seç (varsayılan 1):")
    for k, loc in PRESETS.items():
        print(f"  {k}) {loc.name} ({loc.lat:.4f}, {loc.lon:.4f})")
    choice = input("> ").strip() or "1"
    return PRESETS.get(choice, PRESETS["1"])


def main() -> None:
    print("Horary (Eğlence Modu) — anın ruhu")
    print("-" * 40)
    q = input("Soru (kısa yaz): ").strip()
    if not q:
        q = "Şu anın mesajı ne?"

    loc = prompt_location()
    dt = now_utc()
    snap = build_snapshot(dt, loc)

    print("\n" + "-" * 40)
    print(f"Zaman (UTC): {snap.dt_utc.isoformat(timespec='seconds')}")
    print(f"Konum: {snap.location.name}")
    print("-" * 40)

    print("\nSoru:")
    print(textwrap.fill(q, width=80))
    print("\n" + "-" * 40)
    print(vibe_text(snap))

    print("\n" + "-" * 40)
    print("Mini özet (oyunlaştırma):")
    asc_sign, _ = deg_to_sign_tr(snap.asc)
    moon_sign, _ = deg_to_sign_tr(snap.planets_lon["Ay"])
    print(f"- Tema: {asc_sign} yükselen + {moon_sign} Ay")
    print(f"- Bugünlük motto: ‘{asc_sign} gibi başla, {moon_sign} gibi hisset.’")


if __name__ == "__main__":
    main()

