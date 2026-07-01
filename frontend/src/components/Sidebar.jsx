const LANGUAGES = [
  { id: "qiskit", label: "Qiskit" },
  { id: "qasm2", label: "QASM 2" },
  { id: "qasm3", label: "QASM 3" },
];

export default function Sidebar({ language, onLanguageChange, examples, onLoadExample, activeExampleKey }) {
  return (
    <aside className="w-64 shrink-0 border-r border-slateline bg-slate/40 flex flex-col">
      <div className="px-4 py-4 border-b border-slateline">
        <h1 className="font-display text-lg leading-tight">
          Quantum Circuit<br />Explorer
        </h1>
        <p className="text-xs text-fog mt-1">AI tutor for circuits &amp; simulation</p>
      </div>

      <div className="px-4 py-3 border-b border-slateline">
        <p className="text-xs uppercase tracking-wide text-fog mb-2">Input language</p>
        <div className="flex gap-1 bg-void rounded-md p-1">
          {LANGUAGES.map((l) => (
            <button
              key={l.id}
              onClick={() => onLanguageChange(l.id)}
              className={`flex-1 text-xs py-1.5 rounded-md transition-colors ${
                language === l.id
                  ? "bg-phase0 text-void font-medium"
                  : "text-fog hover:text-mist"
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>

      <div className="px-4 py-3 flex-1 overflow-y-auto">
        <p className="text-xs uppercase tracking-wide text-fog mb-2">Example circuits</p>
        <ul className="space-y-1">
          {Object.entries(examples || {}).map(([key, ex]) => (
            <li key={key}>
              <button
                onClick={() => onLoadExample(key, ex)}
                className={`w-full text-left text-sm px-3 py-2 rounded-md border transition-colors ${
                  activeExampleKey === key
                    ? "border-phase0/60 bg-phase0/10 text-mist"
                    : "border-transparent hover:border-slateline hover:bg-void/60 text-fog"
                }`}
              >
                {key.replaceAll("_", " ")}
                <span className="block text-[10px] text-fog/70">{ex.language}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="px-4 py-3 border-t border-slateline">
        <div className="flex items-center gap-2 text-[11px] text-fog">
          <span className="w-3 h-3 rounded-full phase-wheel inline-block" />
          amplitude phase legend
        </div>
      </div>
    </aside>
  );
}
