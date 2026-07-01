function StatChip({ label, value }) {
  return (
    <div className="bg-void border border-slateline rounded-md px-3 py-2 flex-1">
      <div className="text-[10px] uppercase tracking-wide text-fog">{label}</div>
      <div className="font-mono text-lg text-mist">{value}</div>
    </div>
  );
}

function EntanglementBar({ qubit, entropy }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-6 font-mono text-fog">q{qubit}</span>
      <div className="flex-1 h-2 bg-void rounded-full overflow-hidden border border-slateline">
        <div
          className="h-full bg-phase90 transition-all"
          style={{ width: `${entropy * 100}%` }}
        />
      </div>
      <span className="w-10 text-right font-mono text-fog">{entropy.toFixed(2)}</span>
    </div>
  );
}

export default function AnalysisPanel({ analysis, onAskTutor, explaining }) {
  if (!analysis) {
    return (
      <aside className="w-80 shrink-0 border-l border-slateline bg-slate/40 p-4">
        <p className="text-sm text-fog">Run a circuit to see its analysis here: stats, entanglement, detected patterns, and optimization hints.</p>
      </aside>
    );
  }

  return (
    <aside className="w-80 shrink-0 border-l border-slateline bg-slate/40 flex flex-col overflow-y-auto">
      <div className="p-4 space-y-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-fog mb-2">Circuit stats</p>
          <div className="flex gap-2">
            <StatChip label="Qubits" value={analysis.num_qubits} />
            <StatChip label="Depth" value={analysis.depth} />
            <StatChip label="Gates" value={analysis.total_gates} />
          </div>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-fog mb-2">Entanglement</p>
          <div className="space-y-1.5">
            {Object.entries(analysis.entanglement_entropy_per_qubit).map(([q, e]) => (
              <EntanglementBar key={q} qubit={q} entropy={e} />
            ))}
          </div>
          <p className="text-[11px] text-fog mt-1.5">
            {analysis.entangled
              ? "Non-zero entropy means that qubit can't be described independently of the rest."
              : "All qubits factor into an independent (product) state."}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-fog mb-2">Detected patterns</p>
          {analysis.detected_patterns.length === 0 && (
            <p className="text-xs text-fog">No known algorithm pattern recognized.</p>
          )}
          <div className="space-y-2">
            {analysis.detected_patterns.map((p, i) => (
              <div key={i} className="border border-phase90/30 bg-phase90/5 rounded-md p-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-mist">{p.name}</span>
                  <span className="text-[10px] font-mono text-phase90">{Math.round(p.confidence * 100)}%</span>
                </div>
                <p className="text-[11px] text-fog mt-1 leading-snug">{p.detail}</p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-fog mb-2">Optimization hints</p>
          <ul className="space-y-1.5">
            {analysis.optimization_hints.map((h, i) => (
              <li key={i} className="text-[11px] text-phase270 bg-phase270/5 border border-phase270/20 rounded-md px-2.5 py-2 leading-snug">
                {h}
              </li>
            ))}
          </ul>
        </div>

        <button
          onClick={onAskTutor}
          disabled={explaining}
          className="w-full text-xs font-medium py-2 rounded-md border border-phase0/40 text-phase0 hover:bg-phase0/10 transition-colors disabled:opacity-50"
        >
          {explaining ? "Asking the tutor…" : "Explain this circuit →"}
        </button>
      </div>
    </aside>
  );
}
