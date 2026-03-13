"""
app.py — Horary Astrology Streamlit UI
Kurulum: pip install streamlit pyswisseph anthropic
Çalıştır: streamlit run app.py
"""

import streamlit as st
import datetime
import math
import os
import json

# horary_engine aynı klasörde olmalı
from horary_engine import (
    read_chart, calc_chart, chart_to_dict, build_frawley_prompt,
    ask_claude, PLANET_TR, PLANET_GLYPHS, SIGN_NAMES_TR,
    SIGN_GLYPHS, HOUSE_MEANINGS_TR, ESSENTIAL_DIGNITY_TABLE
)

# ─────────────────────────────────────────
# SAYFA AYARLARI
# ─────────────────────────────────────────

st.set_page_config(
    page_title="Horary · Saat Astrolojisi",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Crimson+Pro:ital,wght@0,300;0,400;1,300;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'Crimson Pro', Georgia, serif;
}
h1, h2, h3 {
    font-family: 'Cinzel', serif !important;
    font-weight: 400 !important;
    letter-spacing: 2px !important;
    color: #c9a84c !important;
}
.stApp {
    background: #0a0912;
}
section[data-testid="stSidebar"] {
    background: #0d0b1a !important;
    border-right: 1px solid rgba(201,168,76,0.15) !important;
}

/* Input alanları */
.stTextArea textarea, .stTextInput input, .stSelectbox select {
    background: rgba(201,168,76,0.04) !important;
    border: 1px solid rgba(201,168,76,0.25) !important;
    color: #e8dfc8 !important;
    font-family: 'Crimson Pro', serif !important;
    font-style: italic !important;
    font-size: 15px !important;
}

/* Buton */
.stButton > button {
    background: transparent !important;
    border: 1px solid #c9a84c !important;
    color: #c9a84c !important;
    font-family: 'Cinzel', serif !important;
    letter-spacing: 2px !important;
    font-size: 13px !important;
    padding: 10px 24px !important;
    transition: all 0.3s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #c9a84c !important;
    color: #0a0912 !important;
}

/* Metric kartları */
[data-testid="metric-container"] {
    background: rgba(201,168,76,0.05) !important;
    border: 1px solid rgba(201,168,76,0.15) !important;
    border-radius: 8px !important;
    padding: 12px !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-family: 'Cinzel', serif !important;
    color: #c9a84c !important;
    font-size: 13px !important;
    letter-spacing: 2px !important;
}

/* Genel metin */
p, li, td, th { color: #d4c49a !important; }
.stMarkdown { color: #d4c49a !important; }

/* Divider */
hr { border-color: rgba(201,168,76,0.2) !important; }

/* Info/success/warning kutuları */
.stAlert { border-radius: 4px !important; }

/* Tab */
.stTabs [data-baseweb="tab"] {
    font-family: 'Cinzel', serif !important;
    letter-spacing: 2px !important;
    font-size: 11px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────

with st.sidebar:
    st.markdown("## ✦ Horary")
    st.markdown("*Saat Astrolojisi · Frawley Yöntemi*")
    st.markdown("---")

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        help="sk-ant-... ile başlar"
    )

    st.markdown("---")
    st.markdown("**Konum**")

    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Enlem", value=42.17, format="%.4f",
                               help="Kuzey + Güney -")
    with col2:
        lon = st.number_input("Boylam", value=42.67, format="%.4f",
                               help="Doğu + Batı -")

    st.markdown("**Tarih & Saat**")
    use_now = st.checkbox("Şu anki zamanı kullan", value=True)

    if use_now:
        dt = datetime.datetime.now()
        st.caption(f"🕐 {dt.strftime('%d.%m.%Y %H:%M')}")
    else:
        date_val = st.date_input("Tarih", value=datetime.date.today())
        time_val = st.time_input("Saat", value=datetime.time(12, 0))
        dt = datetime.datetime.combine(date_val, time_val)

    st.markdown("---")
    st.markdown("**Hakkında**")
    st.caption("John Frawley · The Horary Textbook\nWilliam Lilly geleneği\nRegiomontanus Ev Sistemi")


# ─────────────────────────────────────────
# ANA ALAN
# ─────────────────────────────────────────

st.markdown("# Horary")
st.markdown("*Sorunuzu sorun — yıldızlar bilir, sizi de tanır.*")
st.markdown("---")

# Soru girişi
soru = st.text_area(
    "Sorunuz",
    placeholder="Ne sormak istiyorsunuz? Açık ve net bir soru sorun...",
    height=80,
    label_visibility="collapsed"
)

col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
with col_btn1:
    cast_btn = st.button("✦ Haritayı Çiz", use_container_width=True)

# ─────────────────────────────────────────
# CHART SVG ÇİZİMİ
# ─────────────────────────────────────────

def draw_chart_svg(chart_data: dict, width: int = 500) -> str:
    """Haritayı SVG olarak çiz."""
    cx = cy = width // 2
    Ro = int(width * 0.46)
    Rz = int(width * 0.40)
    Rh = int(width * 0.34)
    Ri = int(width * 0.19)

    def pol(r, deg):
        rad = (deg - 90) * math.pi / 180
        return cx + r * math.cos(rad), cy + r * math.sin(rad)

    svg = [f'<svg width="{width}" height="{width}" viewBox="0 0 {width} {width}" '
           f'xmlns="http://www.w3.org/2000/svg" style="background:#0a0912;border-radius:50%">']

    # Defs — gradients
    svg.append('<defs>')
    svg.append(f'<radialGradient id="bg" cx="50%" cy="50%" r="50%">'
               f'<stop offset="0%" stop-color="#12102a"/>'
               f'<stop offset="100%" stop-color="#0a0912"/></radialGradient>')
    svg.append('</defs>')

    # Background
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{Ro+4}" fill="url(#bg)" '
               f'stroke="rgba(201,168,76,0.3)" stroke-width="1.5"/>')

    # Zodiac burç bantları
    for i in range(12):
        s, e = i * 30, (i + 1) * 30
        x1, y1 = pol(Ro, s)
        x2, y2 = pol(Ro, e)
        x3, y3 = pol(Rz, e)
        x4, y4 = pol(Rz, s)
        fill = "rgba(201,168,76,0.05)" if i % 2 == 0 else "rgba(201,168,76,0.01)"
        svg.append(f'<path d="M{x1:.1f},{y1:.1f} A{Ro},{Ro} 0 0 1 {x2:.1f},{y2:.1f} '
                   f'L{x3:.1f},{y3:.1f} A{Rz},{Rz} 0 0 0 {x4:.1f},{y4:.1f} Z" '
                   f'fill="{fill}" stroke="rgba(201,168,76,0.18)" stroke-width="0.5"/>')
        # Burç sembolü
        gx, gy = pol((Ro + Rz) // 2, s + 15)
        svg.append(f'<text x="{gx:.1f}" y="{gy:.1f}" text-anchor="middle" '
                   f'dominant-baseline="middle" font-size="{int(width*0.038)}" '
                   f'fill="rgba(201,168,76,0.75)">{SIGN_GLYPHS[i]}</text>')
        # Tick
        tx1, ty1 = pol(Rz, s)
        tx2, ty2 = pol(Ro - 2, s)
        svg.append(f'<line x1="{tx1:.1f}" y1="{ty1:.1f}" x2="{tx2:.1f}" y2="{ty2:.1f}" '
                   f'stroke="rgba(201,168,76,0.25)" stroke-width="0.8"/>')

    # Ev çizgileri
    for house in chart_data["houses"]:
        deg = house["longitude"] % 360
        is_angle = house["num"] in [1, 4, 7, 10]
        hx1, hy1 = pol(Rz, deg)
        hx2, hy2 = pol(Ri, deg)
        color = "rgba(200,80,80,0.6)" if is_angle else "rgba(201,168,76,0.2)"
        width_line = "1.5" if is_angle else "0.6"
        dash = "" if is_angle else 'stroke-dasharray="3,3"'
        svg.append(f'<line x1="{hx1:.1f}" y1="{hy1:.1f}" x2="{hx2:.1f}" y2="{hy2:.1f}" '
                   f'stroke="{color}" stroke-width="{width_line}" {dash}/>')
        # Ev numarası
        nx, ny = pol(Rh, deg + 4)
        svg.append(f'<text x="{nx:.1f}" y="{ny:.1f}" text-anchor="middle" '
                   f'dominant-baseline="middle" font-size="{int(width*0.024)}" '
                   f'fill="rgba(201,168,76,0.45)" font-family="Cinzel,serif">{house["num"]}</text>')

    # İç çember
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{Ri}" fill="rgba(10,9,18,0.95)" '
               f'stroke="rgba(201,168,76,0.25)" stroke-width="0.8"/>')

    # Aspect çizgileri (iç çemberde)
    asp_colors = {
        "conjunction": "rgba(201,168,76,0.4)",
        "trine": "rgba(80,160,80,0.35)",
        "sextile": "rgba(80,140,200,0.35)",
        "square": "rgba(180,60,60,0.4)",
        "opposition": "rgba(200,60,60,0.5)",
    }
    for asp in chart_data["aspects"]:
        pa = chart_data["planets"][asp["planet_a"]]
        pb = chart_data["planets"][asp["planet_b"]]
        ax, ay = pol(Ri - int(width * 0.05), pa["longitude"])
        bx, by = pol(Ri - int(width * 0.05), pb["longitude"])
        color = asp_colors.get(asp["aspect"], "rgba(255,255,255,0.1)")
        svg.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" '
                   f'stroke="{color}" stroke-width="0.8"/>')

    # Gezegen noktaları ve sembolleri
    pcolors = {
        "sun": "#f0c040", "moon": "#c0ccf0", "mercury": "#80c080",
        "venus": "#e080b0", "mars": "#e05050", "jupiter": "#c09040", "saturn": "#8090a0"
    }
    for pname, planet in chart_data["planets"].items():
        deg = planet["longitude"]
        color = pcolors.get(pname, "#ffffff")
        # Nokta zodiak bandında
        dx, dy = pol((Rz + Ro) // 2 - 6, deg)
        svg.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="4" fill="{color}" opacity="0.9" '
                   f'stroke="rgba(10,9,18,0.5)" stroke-width="1"/>')
        # Tick
        t1x, t1y = pol(Rz, deg)
        t2x, t2y = pol(Rz + 7, deg)
        svg.append(f'<line x1="{t1x:.1f}" y1="{t1y:.1f}" x2="{t2x:.1f}" y2="{t2y:.1f}" '
                   f'stroke="{color}" stroke-width="1.5"/>')
        # Sembol iç çemberde
        gx, gy = pol(Ri - int(width * 0.07), deg)
        retro = "ℛ" if planet["retrograde"] else ""
        svg.append(f'<text x="{gx:.1f}" y="{gy:.1f}" text-anchor="middle" '
                   f'dominant-baseline="middle" font-size="{int(width*0.038)}" '
                   f'fill="{color}">{planet["glyph"]}{retro}</text>')

    # Merkez — ASC
    svg.append(f'<text x="{cx}" y="{cy+6}" text-anchor="middle" dominant-baseline="middle" '
               f'font-size="{int(width*0.028)}" fill="rgba(201,168,76,0.5)" '
               f'font-family="Cinzel,serif" letter-spacing="2">ASC</text>')

    svg.append('</svg>')
    return "\n".join(svg)


# ─────────────────────────────────────────
# HARITA HESAPLAMA VE GÖSTER
# ─────────────────────────────────────────

if cast_btn and soru.strip():
    if not api_key:
        st.warning("⚠️ API key girilmedi — harita hesaplanacak ama Claude yorumu yapılmayacak.")

    with st.spinner("Harita hesaplanıyor..."):
        try:
            chart = calc_chart(soru, dt, lat, lon)
            chart_data = chart_to_dict(chart)
            prompt = build_frawley_prompt(chart)

            # Session state'e kaydet
            st.session_state["chart_data"] = chart_data
            st.session_state["prompt"] = prompt
            st.session_state["chart_obj"] = chart

            # Claude yorumu
            if api_key:
                with st.spinner("Yıldızlar düşünüyor... 🔮"):
                    interp = ask_claude(prompt, api_key)
                    st.session_state["interpretation"] = interp
            else:
                st.session_state["interpretation"] = None

        except Exception as e:
            st.error(f"Hata: {e}")
            st.stop()

elif cast_btn and not soru.strip():
    st.warning("Lütfen bir soru girin.")


# ─────────────────────────────────────────
# SONUÇLARI GÖSTER
# ─────────────────────────────────────────

if "chart_data" in st.session_state:
    chart_data = st.session_state["chart_data"]
    interp = st.session_state.get("interpretation")

    st.markdown("---")

    # Üst kısım: SVG + Yorum
    col_chart, col_interp = st.columns([1, 1])

    with col_chart:
        st.markdown("### Harita")
        svg = draw_chart_svg(chart_data, width=480)
        st.components.v1.html(
            f'<div style="display:flex;justify-content:center;background:#0a0912;padding:16px;border-radius:8px;">{svg}</div>',
            height=520
        )

    with col_interp:
        st.markdown("### Yorum")
        if interp:
            st.markdown(
                f'<div style="background:rgba(201,168,76,0.05);border:1px solid rgba(201,168,76,0.2);'
                f'border-radius:8px;padding:20px;font-style:italic;font-size:15px;line-height:1.9;'
                f'color:#e8dfc8;min-height:300px;">{interp}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="background:rgba(201,168,76,0.03);border:1px solid rgba(201,168,76,0.1);'
                'border-radius:8px;padding:20px;color:rgba(201,168,76,0.4);font-style:italic;'
                'text-align:center;min-height:300px;display:flex;align-items:center;justify-content:center;">'
                'API key ekleyin, yorum gelsin.</div>',
                unsafe_allow_html=True
            )

        # Soru tipi badge
        from horary_engine import detect_question_type
        q_data = detect_question_type(st.session_state.get("prompt", ""))
        st.caption(f"🕐 {chart_data['datetime'][:16].replace('T',' ')} · "
                   f"{'Gündüz ☀️' if chart_data['is_daytime'] else 'Gece 🌙'}")

    st.markdown("---")

    # Alt kısım: detay tablar
    tab1, tab2, tab3, tab4 = st.tabs(["GEZEGENLER", "EVLER", "ASPECTLER", "PROMPT"])

    with tab1:
        st.markdown("#### Gezegen Pozisyonları")
        dignity_colors = {
            "domicile": "🟢", "exaltation": "🟡", "triplicity": "🔵",
            "face": "⚪", "peregrine": "⚫", "detriment": "🔴", "fall": "🟠"
        }
        for pname, p in chart_data["planets"].items():
            retro = " ℞" if p["retrograde"] else ""
            dig_icon = dignity_colors.get(p["dignity"], "⚫")
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 2])
            with col1: st.markdown(f"**{p['glyph']}**")
            with col2: st.markdown(f"{p['name_tr']}{retro}")
            with col3: st.markdown(f"{p['degree']}°{p['minute']:02d}′ {p['sign_glyph']} {p['sign']}")
            with col4: st.markdown(f"Ev **{p['house']}**")
            with col5: st.markdown(f"{dig_icon} {p['dignity']} ({p['dignity_score']:+d})")

    with tab2:
        st.markdown("#### Ev Başlangıçları · Regiomontanus")
        for h in chart_data["houses"]:
            is_angle = h["num"] in [1, 4, 7, 10]
            prefix = "**" if is_angle else ""
            suffix = "**" if is_angle else ""
            col1, col2, col3, col4 = st.columns([1, 2, 2, 3])
            with col1: st.markdown(f"{prefix}Ev {h['num']}{suffix}")
            with col2: st.markdown(f"{h['degree']}°{h['minute']:02d}′ {h['sign_glyph']} {h['sign']}")
            with col3: st.markdown(f"Yön: {h['ruler_tr']}")
            with col4: st.caption(h["meaning"])

    with tab3:
        st.markdown("#### Açısal İlişkiler")
        asp_symbols = {
            "conjunction": "☌", "trine": "△", "sextile": "✶",
            "square": "□", "opposition": "☍"
        }
        if chart_data["aspects"]:
            for asp in chart_data["aspects"]:
                pa = chart_data["planets"][asp["planet_a"]]
                pb = chart_data["planets"][asp["planet_b"]]
                app_str = "→ yaklaşıyor" if asp["applying"] else "← uzaklaşıyor"
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.markdown(f"{pa['glyph']} {pa['name_tr']} "
                                f"**{asp_symbols[asp['aspect']]}** "
                                f"{pb['glyph']} {pb['name_tr']}")
                with col2: st.caption(f"orb: {asp['orb']:.1f}°")
                with col3: st.caption(app_str)
        else:
            st.info("Önemli aspect bulunamadı.")

    with tab4:
        st.markdown("#### Claude'a Giden Prompt")
        st.caption("Frawley kurallarıyla oluşturulan harita özeti")
        st.text_area("", value=st.session_state.get("prompt", ""), height=400,
                     label_visibility="collapsed")

elif not cast_btn:
    # Hoş geldin ekranı
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:rgba(201,168,76,0.4);">
        <div style="font-size:48px;margin-bottom:16px;">🔮</div>
        <div style="font-family:'Cinzel',serif;font-size:16px;letter-spacing:3px;margin-bottom:8px;">
            SORUNUZU YAZIN
        </div>
        <div style="font-style:italic;font-size:14px;">
            Haritayı çiz butonuna basın — yıldızlar okusun.
        </div>
    </div>
    """, unsafe_allow_html=True)
