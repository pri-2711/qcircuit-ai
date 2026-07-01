const BASE = "/api";

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || `Request to ${path} failed (${res.status})`);
  }
  return data;
}

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Request to ${path} failed (${res.status})`);
  return data;
}

export const api = {
  examples: () => get("/examples"),
  simulate: (code, language) => post("/simulate", { code, language }),
  analyze: (code, language) => post("/analyze", { code, language }),
  explain: (code, language, question) => post("/explain", { code, language, question }),
  chat: (messages, code, language) => post("/chat", { messages, code, language }),
};
