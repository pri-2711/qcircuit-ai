import Editor from "@monaco-editor/react";

export default function CodeEditor({ code, onChange, language, onRun, running, error }) {
  const monacoLang = language === "qiskit" ? "python" : "plaintext";

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-2 border-b border-slateline bg-slate/40">
        <span className="text-xs text-fog font-mono">circuit.{language === "qiskit" ? "py" : "qasm"}</span>
        <button
          onClick={onRun}
          disabled={running}
          className="text-xs font-medium px-3 py-1.5 rounded-md bg-phase0 text-void hover:brightness-110 disabled:opacity-50 transition-all"
        >
          {running ? "Running…" : "Run simulation"}
        </button>
      </div>
      <div className="flex-1 min-h-0">
        <Editor
          height="100%"
          language={monacoLang}
          theme="vs-dark"
          value={code}
          onChange={(v) => onChange(v ?? "")}
          options={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: 13,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            padding: { top: 12 },
          }}
        />
      </div>
      {error && (
        <div className="px-4 py-2 text-xs font-mono text-phase180 bg-phase180/10 border-t border-phase180/30">
          {error}
        </div>
      )}
    </div>
  );
}
