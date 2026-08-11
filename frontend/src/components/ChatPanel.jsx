import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

export default function ChatPanel({ messages, onSend, sending }) {
  const [draft, setDraft] = useState("");

  const submit = () => {
    if (!draft.trim()) return;
    onSend(draft.trim());
    setDraft("");
  };

  const Code = ({ inline, children, className }) => {
    if (inline) return <code className="bg-void px-1 py-0.5 rounded text-xs">{children}</code>;
    return (
      <pre className="bg-void p-2 rounded border border-slateline overflow-auto text-xs">
        <code>{children}</code>
      </pre>
    );
  };

  return (
    <div className="border-t border-slateline bg-slate/40 flex flex-col h-full">
      <div className="px-4 py-1.5 text-xs uppercase tracking-wide text-fog border-b border-slateline">
        Ask the tutor
      </div>
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-2">
        {messages.length === 0 && (
          <p className="text-xs text-fog">
            Ask about the gates you're using, why (or whether) your circuit is entangled, or what
            algorithm it resembles.
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`text-xs leading-relaxed max-w-[85%] rounded-md px-3 py-2 whitespace-pre-wrap prose prose-invert prose-sm ${
              m.role === "user"
                ? "bg-phase0/10 border border-phase0/30 ml-auto text-mist"
                : "bg-void border border-slateline text-mist"
            }`}
          >
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[rehypeKatex]}
              components={{ code: Code }}
            >
              {m.content}
            </ReactMarkdown>
          </div>
        ))}
        {sending && <p className="text-xs text-fog">Thinking…</p>}
      </div>
      <div className="p-2 border-t border-slateline flex gap-2">
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="e.g. why is this entangled?"
          className="flex-1 bg-void border border-slateline rounded-md px-3 py-1.5 text-xs text-mist placeholder:text-fog/60 focus:outline-none focus:border-phase0/50"
        />
        <button
          onClick={submit}
          className="text-xs font-medium px-3 py-1.5 rounded-md bg-phase0 text-void hover:brightness-110 transition-all"
        >
          Send
        </button>
      </div>
    </div>
  );
}
