import { useState } from "react";

const phases = [
  {
    name: "Menstrüasyon",
    days: "1-5. gün",
    range: [0, 5],
    color: "#c0392b",
    lightColor: "#fadbd8",
    hormones: { östrojen: 10, progesteron: 5, lh: 8, fsh: 15 },
    description: "Rahim duvarı dökülür. Östrojen & progesteron en düşük seviyede.",
    symptoms: ["Kramp", "Yorgunluk", "Düşük enerji"],
    emoji: "🩸"
  },
  {
    name: "Foliküler Faz",
    days: "1-13. gün",
    range: [1, 13],
    color: "#e67e22",
    lightColor: "#fdebd0",
    hormones: { östrojen: 60, progesteron: 8, lh: 20, fsh: 40 },
    description: "FSH folikül olgunlaştırır. Östrojen yavaş yavaş yükselir. Enerji artar!",
    symptoms: ["Artan enerji", "İyimserlik", "Libido artışı", "Net düşünce"],
    emoji: "🌱"
  },
  {
    name: "Ovülasyon",
    days: "~14. gün",
    range: [13, 16],
    color: "#f1c40f",
    lightColor: "#fef9e7",
    hormones: { östrojen: 90, progesteron: 15, lh: 95, fsh: 60 },
    description: "LH zirvesi! Yumurta serbest kalır. Östrojen en yüksek noktada.",
    symptoms: ["Pik enerji", "Sosyal hissetme", "Hafif karın ağrısı mümkün"],
    emoji: "🥚"
  },
  {
    name: "Luteal Faz",
    days: "15-28. gün",
    range: [15, 28],
    color: "#8e44ad",
    lightColor: "#f5eef8",
    hormones: { östrojen: 45, progesteron: 85, lh: 10, fsh: 8 },
    description: "Sarı cisim (corpus luteum) oluşur → PROGESTERON yükselir. Gebelik yoksa düşer, döngü başlar.",
    symptoms: ["İştah artışı", "Şişkinlik", "Yorgunluk", "PMS belirtileri", "Sıcaklık artışı"],
    emoji: "🌙"
  }
];

const hormoneColors = {
  östrojen: "#e74c3c",
  progesteron: "#8e44ad",
  lh: "#3498db",
  fsh: "#27ae60"
};

export default function CycleChart() {
  const [active, setActive] = useState(3);

  const phase = phases[active];

  const chartPoints = {
    östrojen: [10, 20, 35, 60, 90, 70, 45, 40, 30, 20, 15, 10],
    progesteron: [5, 5, 6, 7, 15, 30, 55, 85, 80, 60, 30, 10],
    lh: [8, 8, 10, 15, 95, 20, 12, 10, 9, 8, 8, 8],
    fsh: [15, 25, 35, 40, 60, 30, 15, 8, 8, 8, 8, 10]
  };

  const toPath = (points, w, h) => {
    const step = w / (points.length - 1);
    return points.map((v, i) => `${i === 0 ? "M" : "L"} ${i * step} ${h - (v / 100) * h}`).join(" ");
  };

  const dayMarkers = [1, 5, 10, 14, 16, 20, 24, 28];

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
      fontFamily: "'Georgia', serif",
      padding: "24px 16px",
      color: "white"
    }}>
      <div style={{ maxWidth: 720, margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{ fontSize: 12, letterSpacing: 4, color: "#a29bfe", textTransform: "uppercase", marginBottom: 8 }}>
            28 Günlük Döngü
          </div>
          <h1 style={{ fontSize: 28, fontWeight: "normal", margin: 0, letterSpacing: 1 }}>
            Adetin Dört Fazı
          </h1>
        </div>

        <div style={{ marginBottom: 24 }}>
          <div style={{ display: "flex", borderRadius: 12, overflow: "hidden", height: 52, boxShadow: "0 4px 20px rgba(0,0,0,0.4)" }}>
            {phases.map((p, i) => {
              const width = ((p.range[1] - p.range[0]) / 27) * 100;
              return (
                <button key={i} onClick={() => setActive(i)} style={{
                  width: `${width}%`,
                  background: active === i ? p.color : p.color + "66",
                  border: "none", cursor: "pointer",
                  display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                  transition: "all 0.3s", fontSize: 10, color: "white",
                  fontWeight: active === i ? "bold" : "normal", gap: 2
                }}>
                  <span style={{ fontSize: 16 }}>{p.emoji}</span>
                  <span style={{ fontSize: 9, opacity: 0.9 }}>{p.days}</span>
                </button>
              );
            })}
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4, fontSize: 10, color: "#74b9ff", opacity: 0.7 }}>
            {dayMarkers.map(d => <span key={d}>{d}. gün</span>)}
          </div>
        </div>

        <div style={{
          background: "rgba(255,255,255,0.05)", borderRadius: 16, padding: "20px 16px 12px",
          marginBottom: 20, backdropFilter: "blur(10px)", border: "1px solid rgba(255,255,255,0.1)"
        }}>
          <div style={{ fontSize: 11, color: "#dfe6e9", marginBottom: 12, letterSpacing: 2, textTransform: "uppercase" }}>
            Hormon Seviyeleri
          </div>
          <svg width="100%" viewBox="0 0 400 120" style={{ overflow: "visible" }}>
            {[0, 25, 50, 75, 100].map(v => (
              <line key={v} x1="0" y1={120 - v * 1.2} x2="400" y2={120 - v * 1.2}
                stroke="rgba(255,255,255,0.07)" strokeWidth="1" />
            ))}
            <rect x={phases[active].range[0] / 27 * 400} y={0}
              width={(phases[active].range[1] - phases[active].range[0]) / 27 * 400}
              height={120} fill={phases[active].color + "22"} />
            {Object.entries(chartPoints).map(([h, pts]) => (
              <path key={h} d={toPath(pts, 400, 120)} fill="none"
                stroke={hormoneColors[h]} strokeWidth={h === "progesteron" || h === "östrojen" ? 2.5 : 1.5}
                opacity={0.85} strokeLinejoin="round" strokeLinecap="round" />
            ))}
          </svg>
          <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginTop: 8 }}>
            {Object.entries(hormoneColors).map(([h, c]) => (
              <div key={h} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11 }}>
                <div style={{ width: 20, height: 3, background: c, borderRadius: 2 }} />
                <span style={{ color: "#dfe6e9", textTransform: "capitalize" }}>{h}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={{
          background: `linear-gradient(135deg, ${phase.color}33, ${phase.color}11)`,
          border: `1px solid ${phase.color}55`, borderRadius: 16, padding: 20, backdropFilter: "blur(10px)"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
            <span style={{ fontSize: 32 }}>{phase.emoji}</span>
            <div>
              <div style={{ fontSize: 20, fontWeight: "bold", color: phase.color }}>{phase.name}</div>
              <div style={{ fontSize: 13, color: "#b2bec3" }}>{phase.days}</div>
            </div>
          </div>
          <p style={{ margin: "0 0 16px", fontSize: 14, lineHeight: 1.7, color: "#dfe6e9" }}>
            {phase.description}
          </p>
          <div>
            <div style={{ fontSize: 11, color: "#a29bfe", letterSpacing: 2, textTransform: "uppercase", marginBottom: 8 }}>
              Tipik Belirtiler
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {phase.symptoms.map(s => (
                <span key={s} style={{
                  background: phase.color + "33", border: `1px solid ${phase.color}55`,
                  borderRadius: 20, padding: "4px 12px", fontSize: 12, color: "white"
                }}>{s}</span>
              ))}
            </div>
          </div>
        </div>

        <div style={{ textAlign: "center", marginTop: 20, fontSize: 11, color: "#636e72", lineHeight: 1.6 }}>
          Mirena ile luteal faz progesteronu düşük kalır ama foliküler ve ovülatuar faz<br />
          östrojenin etkisi devam edebilir. Döngü kişiden kişiye değişir.
        </div>
      </div>
    </div>
  );
}