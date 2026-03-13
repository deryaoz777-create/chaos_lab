from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Tuple

import swisseph as swe


SIGNS_TR = [
    "Koç",
    "Boğa",
    "İkizler",
    "Yengeç",
    "Aslan",
    "Başak",
    "Terazi",
    "Akrep",
    "Yay",
    "Oğlak",
    "Kova",
    "Balık",
]


@dataclass(frozen=True)
class Location:
    name: str
    lat: float
    lon: float


@dataclass(frozen=True)
class PlanetPos:
    name: str
    lon: float  # ecliptic longitude, degrees 0..360


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def julian_day(dt_utc: datetime) -> float:
    if dt_utc.tzinfo is None:
        raise ValueError("dt_utc must be timezone-aware (UTC).")
    dt_utc = dt_utc.astimezone(timezone.utc)
    hour = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600 + dt_utc.microsecond / 3_600_000_000
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour)


def deg_to_sign_tr(deg: float) -> Tuple[str, float]:
    d = deg % 360.0
    idx = int(d // 30)
    return SIGNS_TR[idx], d % 30.0


def fmt_sign_deg_tr(deg: float) -> str:
    sign, within = deg_to_sign_tr(deg)
    return f"{sign} {within:.2f}°"


def houses_regiomontanus(jd: float, loc: Location) -> Tuple[List[float], float]:
    cusps, ascmc = swe.houses(jd, loc.lat, loc.lon, b"R")
    asc = float(ascmc[0])
    return [float(x) for x in cusps], asc


def planet_positions(jd: float, planet_map: Dict[str, int]) -> List[PlanetPos]:
    out: List[PlanetPos] = []
    for name, code in planet_map.items():
        pos, _ = swe.calc_ut(jd, code)
        out.append(PlanetPos(name=name, lon=float(pos[0]) % 360.0))
    return out


def angular_distance(a: float, b: float) -> float:
    """Smallest distance in degrees between two longitudes."""
    d = abs((a - b) % 360.0)
    return d if d <= 180 else 360.0 - d


def aspect(a: float, b: float, orb: float = 6.0) -> Tuple[str, float] | None:
    """Return (aspect_name, exactness_deg) if within orb for major aspects."""
    d = angular_distance(a, b)
    aspects = {
        "kavuşum": 0.0,
        "sekstil": 60.0,
        "kare": 90.0,
        "üçgen": 120.0,
        "karşıt": 180.0,
    }
    best_name = None
    best_delta = None
    for name, target in aspects.items():
        delta = abs(d - target)
        if delta <= orb and (best_delta is None or delta < best_delta):
            best_name, best_delta = name, delta
    if best_name is None:
        return None
    return best_name, float(best_delta)


def house_of_degree(deg: float, cusps: Iterable[float]) -> int:
    """
    Determine house number (1..12) for a longitude given 12 cusp longitudes.
    Handles 360 wrap-around.
    """
    c = [float(x) % 360.0 for x in cusps]
    d = float(deg) % 360.0
    for i in range(12):
        start = c[i]
        end = c[(i + 1) % 12]
        if start <= end:
            if start <= d < end:
                return i + 1
        else:
            # wrap-around house (e.g., 350° -> 20°)
            if d >= start or d < end:
                return i + 1
    return 1

