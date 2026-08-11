import { useState } from "react";

export default function ChatPanel({ messages, onSend, sending }) {
  const [draft, setDraft] = useState("");

  const submit = () => {
    if (!draft.trim()) return;
    onSend(draft.trim());
    setDraft("");
  };

  // Minimal markdown-like renderer: handles $$...$$ blocks, **bold**, and simple lists
  const renderMarkdown = (text) => {
    if (!text) return "";
    const escapeHtml = (s) =>
      s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

    // Split $$...$$ blocks
    const parts = text.split(/(\$\$[\s\S]*?\$\$)/g);
    const htmlParts = parts.map((part) => {
      if (part.startsWith("$$") && part.endsWith("$$")) {
        const inner = part.slice(2, -2).trim();
        return `<pre class="font-mono text-xs whitespace-pre-wrap p-2 bg-void border border-slateline rounded-md">${escapeHtml(inner)}</pre>`;
      }
      // inline **bold**
      let escaped = escapeHtml(part).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
      const lines = escaped.split(/\r?\n/);
      let inList = false;
      let out = [];
      lines.forEach((ln) => {
        if (ln.trim().match(/^([*-])\s+/)) {
          if (!inList) {
            inList = true;
            out.push("<ul class='list-disc pl-5'>");
          }
          out.push(`<li>${ln.replace(/^([*-])\s+/, "")}</li>`);
        } else {
          if (inList) {
            inList = false;
            out.push("</ul>");
          }
          if (ln.trim() === "") out.push("<br/>");
          else out.push(`<p class='my-1'>${ln}</p>`);
        }
      });
      if (inList) out.push("</ul>");
      return out.join("");
    });
    return htmlParts.join("");
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
            className={`text-xs leading-relaxed max-w-[85%] rounded-md px-3 py-2 whitespace-pre-wrap prose prose-invert prose-xs ${
              m.role === "user"
                ? "bg-phase0/10 border border-phase0/30 ml-auto text-mist"
                : "bg-void border border-slateline text-mist"
            }`}
            dangerouslySetInnerHTML={{ __html: renderMarkdown(m.content) }}
          />
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
