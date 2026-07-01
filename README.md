# Quantum Circuit Explorer & AI Tutor

A working MVP scaffold: write or paste a Qiskit/OpenQASM circuit, simulate it,
see its diagram/statevector/probabilities, get automatic entanglement +
algorithm-pattern detection (Bell, GHZ, QFT, Grover, VQE-style ansätze),
optimization hints, and ask a tutor to explain it.

Everything below has been run and verified in this environment: backend
endpoints tested end-to-end (including the security sandbox and timeout),
frontend built with `npm run build` with zero errors, and the two talking to
each other over a live HTTP request through the real Vite dev proxy.

## Quick start (two terminals)

```bash
# Terminal 1 -- backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 -- frontend
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Pick an example circuit from the sidebar (or
write your own), hit **Run simulation**, and explore the Diagram /
Statevector / Probabilities tabs plus the analysis panel on the right.

No API keys are required to run it -- `/api/explain` and `/api/chat` work out
of the box using a template explainer grounded in the real analysis JSON.
Add `OPENAI_API_KEY` or `GEMINI_API_KEY` to `backend/.env` (see
`backend/.env.example`) to upgrade those two endpoints to a real LLM call.

## What's implemented vs. stubbed

| Feature from the original brief                        | Status |
|----------------------------------------------------------|--------|
| Qiskit + OpenQASM 2/3 input                               | ✅ working |
| Cirq support                                              | not started (see "Extending" in each README) |
| Interactive editor + circuit diagram                       | ✅ working (Monaco + Qiskit's mpl drawer) |
| Statevector + measurement probabilities                    | ✅ working |
| Entanglement detection                                     | ✅ working (per-qubit reduced-state entropy) |
| Bell / GHZ detection                                       | ✅ working (statevector-signature based) |
| QFT / Grover / VQE detection                                | ⚠️ heuristic only -- name/structure matching, not a real pattern-matching engine |
| Circuit stats (depth, gate counts)                          | ✅ working |
| Optimization suggestions                                    | ✅ basic (transpile-diff + adjacent-inverse-gate detection) |
| AI explanations                                            | ✅ template mode always on; LLM mode if you add an API key |
| Conversational tutor                                        | ✅ same as above |
| Circuit similarity search / automated design (future work)   | not started -- `analyzer.py`'s docstring marks where it plugs in |

## Repo layout

```
quantum-explorer/
├── backend/     FastAPI + Qiskit -- see backend/README.md
└── frontend/    React + Vite + Tailwind + Monaco -- see frontend/README.md
```

## Suggested next steps, roughly in order of leverage

1. **Swap the pattern-detection heuristics for something more rigorous.**
   Right now QFT/Grover/VQE detection is name/structure matching, which breaks
   the moment someone writes the same algorithm without using the library's
   named building blocks. A gate-sequence or DAG-embedding similarity search
   against a small curated library of canonical circuits would generalize much
   better, and is exactly the "future research" direction flagged in the brief.
2. **Containerize the code-execution sandbox.** The current subprocess-based
   sandbox in `execution.py` is fine for a single trusted local user, but treat
   it as decoration, not a security boundary, before any shared/public
   deployment -- run it in gVisor/Firecracker/a locked-down Docker container
   with no network and a resource limit instead.
3. **Add Cirq.** Both READMEs point at the exact seam: a `circuit_from_cirq_source`
   next to the Qiskit one, and a `"cirq"` case in the frontend's language tabs.
4. **Persistence.** There's currently no database -- nothing is saved between
   page loads. If you want saved circuits, history, or shareable links, that's
   the next structural addition (Postgres + a `circuits` table would be enough
   to start).
5. **Real LLM tool-calling.** `explainer.py` is a good foundation but doesn't let
   the model act (e.g. "let me try removing that gate and re-simulating" ) --
   that's where LangChain/LangGraph earns its keep, per the original brief.
