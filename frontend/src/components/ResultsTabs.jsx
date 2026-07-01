import { useState } from "react";

const TABS = ["Diagram", "Statevector", "Probabilities"];

// Map a phase angle (radians) to the same 4-anchor hue convention used across the UI.
function phaseColor(re, im) {
  const angle = Math.atan2(im, re); // -pi..pi
  const deg = ((angle * 180) / Math.PI + 360) % 360;
  const anchors = [
    [0, 79, 216, 235],    // phase0  #4FD8EB
    [90, 185, 142, 255],  // phase90 #B98EFF
    [180, 255, 123, 114], // phase180 #FF7B72
    [270, 255, 196, 107], // phase270 #FFC46B
    [360, 79, 216, 235],
  ];
  for (let i = 0; i < anchors.length - 1; i++) {
    const [d0, r0, g0, b0] = anchors[i];
    const [d1, r1, g1, b1] = anchors[i + 1];
    if (deg >= d0 && deg <= d1) {
      const t = (deg - d0) / (d1 - d0);
      const r = Math.round(r0 + (r1 - r0) * t);
      const g = Math.round(g0 + (g1 - g0) * t);
      const b = Math.round(b0 + (b1 - b0) * t);
      return `rgb(${r},${g},${b})`;
    }
  }
  return "#4FD8EB";
}

function Bar({ label, value, color, sublabel }) {
  return (
    <div className="flex items-center gap-3 py-1">
      <span className="w-16 text-xs font-mono text-fog shrink-0">|{label}⟩</span>
      <div className="flex-1 h-5 bg-void rounded-sm overflow-hidden border border-slateline">
        <div
          className="h-full transition-all"
          style={{ width: `${Math.max(value * 100, 1.5)}%`, background: color }}
        />
      </div>
      <span className="w-24 text-xs font-mono text-fog text-right shrink-0">{sublabel}</span>
    </div>
  );
}

export default function ResultsTabs({ simResult }) {
  const [tab, setTab] = useState("Diagram");

  return (
    <div className="flex flex-col h-full">
      <div className="flex border-b border-slateline bg-slate/40">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`text-xs px-4 py-2 border-b-2 transition-colors ${
              tab === t ? "border-phase0 text-mist" : "border-transparent text-fog hover:text-mist"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {!simResult && (
          <p className="text-sm text-fog">Run the circuit to see its diagram, statevector, and measurement outcomes.</p>
        )}

        {simResult && tab === "Diagram" && (
          <img
            src={`data:image/png;base64,${simResult.diagram_png_base64}`}
            alt="Circuit diagram"
            className="max-w-full bg-white rounded-md p-2"
          />
        )}

        {simResult && tab === "Statevector" && (
          <div>
            <p className="text-xs text-fog mb-3">
              Amplitude bar length = magnitude, color = phase angle (see legend, top left).
            </p>
            {simResult.basis_labels.map((label, i) => {
              const re = simResult.statevector_real[i];
              const im = simResult.statevector_imag[i];
              const mag = Math.sqrt(re * re + im * im);
              if (mag < 1e-6) return null;
              return (
                <Bar
                  key={label}
                  label={label}
                  value={mag}
                  color={phaseColor(re, im)}
                  sublabel={`${re.toFixed(3)} ${im >= 0 ? "+" : "-"} ${Math.abs(im).toFixed(3)}i`}
                />
              );
            })}
          </div>
        )}

        {simResult && tab === "Probabilities" && (
          <div>
            {Object.entries(simResult.probabilities)
              .sort((a, b) => b[1] - a[1])
              .map(([label, p]) => (
                <Bar key={label} label={label} value={p} color="#4FD8EB" sublabel={`${(p * 100).toFixed(1)}%`} />
              ))}
          </div>
        )}
      </div>
    </div>
  );
}
