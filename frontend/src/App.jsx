import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import CodeEditor from "./components/CodeEditor.jsx";
import ResultsTabs from "./components/ResultsTabs.jsx";
import AnalysisPanel from "./components/AnalysisPanel.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import { api } from "./api.js";

const FALLBACK_EXAMPLE = {
  language: "qiskit",
  code: "qc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure_all()\n",
};

export default function App() {
  const [examples, setExamples] = useState({});
  const [activeExampleKey, setActiveExampleKey] = useState(null);
  const [language, setLanguage] = useState("qiskit");
  const [code, setCode] = useState(FALLBACK_EXAMPLE.code);

  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState(null);
  const [simResult, setSimResult] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const [explaining, setExplaining] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [sending, setSending] = useState(false);
  const [backendUnreachable, setBackendUnreachable] = useState(false);
  const [chatHeight, setChatHeight] = useState(224); // px, default ~h-56
  const [editorHeight, setEditorHeight] = useState(320);

  useEffect(() => {
    api
      .examples()
      .then((ex) => {
        setExamples(ex);
        const first = Object.entries(ex)[0];
        if (first) {
          setActiveExampleKey(first[0]);
          setLanguage(first[1].language);
          setCode(first[1].code);
        }
      })
      .catch(() => setBackendUnreachable(true));
  }, []);

  const loadExample = (key, ex) => {
    setActiveExampleKey(key);
    setLanguage(ex.language);
    setCode(ex.code);
    setSimResult(null);
    setAnalysis(null);
    setRunError(null);
  };

  const run = async () => {
    setRunning(true);
    setRunError(null);
    setBackendUnreachable(false);
    try {
      const [sim, an] = await Promise.all([
        api.simulate(code, language),
        api.analyze(code, language),
      ]);
      setSimResult(sim);
      setAnalysis(an);
    } catch (e) {
      setRunError(e.message);
      setSimResult(null);
      setAnalysis(null);
      if (e.message?.includes("Failed to fetch")) setBackendUnreachable(true);
    } finally {
      setRunning(false);
    }
  };

  const askTutor = async () => {
    setExplaining(true);
    try {
      const res = await api.explain(code, language, "Explain this circuit.");
      setChatMessages((prev) => [...prev, { role: "assistant", content: res.explanation }]);
    } catch (e) {
      setChatMessages((prev) => [...prev, { role: "assistant", content: `Couldn't generate an explanation: ${e.message}` }]);
    } finally {
      setExplaining(false);
    }
  };

  const sendChat = async (text) => {
    const next = [...chatMessages, { role: "user", content: text }];
    setChatMessages(next);
    setSending(true);
    try {
      const res = await api.chat(next, code, language);
      setChatMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
    } catch (e) {
      setChatMessages((prev) => [...prev, { role: "assistant", content: `Error: ${e.message}` }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-void text-mist font-sans">
      {backendUnreachable && (
        <div className="bg-phase180/10 border-b border-phase180/30 text-phase180 text-xs px-4 py-2 font-mono">
          Can't reach the backend at /api. Start it with: cd backend &amp;&amp; uvicorn app.main:app --reload
        </div>
      )}
      <div className="flex flex-1 min-h-0">
        <Sidebar
          language={language}
          onLanguageChange={setLanguage}
          examples={examples}
          onLoadExample={loadExample}
          activeExampleKey={activeExampleKey}
        />

        <main className="flex-1 min-w-0 flex flex-col">
          <div style={{ height: editorHeight }} className="min-h-0">
            <CodeEditor
              code={code}
              onChange={setCode}
              language={language}
              onRun={run}
              running={running}
              error={runError}
            />
          </div>

          <div
            onMouseDown={(e) => {
              e.preventDefault();
              const startY = e.clientY;
              const startH = editorHeight;
              const onMove = (ev) => {
                const dy = ev.clientY - startY; // positive when dragging down
                const next = Math.max(120, Math.min(window.innerHeight - 200, startH + dy));
                setEditorHeight(next);
              };
              const onUp = () => {
                window.removeEventListener("mousemove", onMove);
                window.removeEventListener("mouseup", onUp);
              };
              window.addEventListener("mousemove", onMove);
              window.addEventListener("mouseup", onUp);
            }}
            className="h-2 cursor-row-resize bg-slate/20"
            title="Drag to resize code editor"
          />

          <div className="border-t border-slateline min-h-0 flex-1">
            <ResultsTabs simResult={simResult} />
          </div>
        </main>

        <div className="flex flex-col w-80 shrink-0">
          <div className="flex-1 min-h-0 overflow-y-auto">
            <AnalysisPanel analysis={analysis} onAskTutor={askTutor} explaining={explaining} />
          </div>
        </div>
      </div>
      <div className="flex-shrink-0">
        <div
          onMouseDown={(e) => {
            e.preventDefault();
            const startY = e.clientY;
            const startH = chatHeight;
            const onMove = (ev) => {
              const dy = startY - ev.clientY; // positive when dragging up
              const next = Math.max(100, Math.min(900, startH + dy));
              setChatHeight(next);
            };
            const onUp = () => {
              window.removeEventListener("mousemove", onMove);
              window.removeEventListener("mouseup", onUp);
            };
            window.addEventListener("mousemove", onMove);
            window.addEventListener("mouseup", onUp);
          }}
          className="h-2 cursor-row-resize bg-slate/20"
          title="Drag to resize tutor"
        />

        <div style={{ height: chatHeight }} className="border-t border-slateline bg-slate/40">
          <ChatPanel messages={chatMessages} onSend={sendChat} sending={sending} />
        </div>
      </div>
    </div>
  );
}
