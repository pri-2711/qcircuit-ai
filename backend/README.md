# Backend -- Quantum Circuit Explorer API

FastAPI service that parses, simulates, analyzes, and explains quantum
circuits written in Qiskit Python, OpenQASM 2, or OpenQASM 3.

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # optional: add OPENAI_API_KEY or GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive Swagger UI once it's running.

## Endpoints

| Method | Path            | Purpose                                                        |
|--------|-----------------|------------------------------------------------------------------|
| GET    | `/api/health`   | Liveness check                                                  |
| GET    | `/api/examples` | Built-in example circuits (Bell, GHZ, etc.)                     |
| POST   | `/api/parse`    | Source -> unified intermediate representation                   |
| POST   | `/api/simulate` | Statevector, measurement probabilities, circuit diagram (PNG)   |
| POST   | `/api/analyze`  | Stats, entanglement, algorithm-pattern detection, optimization  |
| POST   | `/api/explain`  | Natural-language explanation of a circuit (LLM or template)     |
| POST   | `/api/chat`     | Multi-turn conversational tutor, grounded in circuit analysis   |

All the `POST` endpoints (except `/api/chat`) take:
```json
{ "code": "qc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n", "language": "qiskit" }
```
`language` is one of `"qiskit"`, `"qasm2"`, `"qasm3"`.

## How each piece works

- **`app/execution.py`** -- turns source into a `QuantumCircuit`. The Qiskit-Python
  path runs user code in a **forked subprocess** with a restricted builtin/import
  whitelist and a wall-clock timeout, so a hang, crash, or fork-bomb in submitted
  code can't take the API server down. **This is a dev-grade sandbox, not a
  production security boundary** -- see the security note at the top of that file
  before exposing this behind a public URL.
- **`app/simulator.py`** -- ideal (noiseless) statevector simulation via
  `qiskit.quantum_info.Statevector`. No `qiskit-aer` dependency needed for this;
  swap it in later if you add noise models.
- **`app/analyzer.py`** -- circuit stats, per-qubit entanglement entropy, and
  algorithm-pattern detection (Bell/GHZ via statevector signature, QFT/Grover/VQE
  via gate-name and structural heuristics). Optimization hints currently come from
  comparing `qiskit.transpile(..., optimization_level=3)` against the original.
- **`app/explainer.py`** -- template-based explanation generator (always available,
  zero-config) with an optional upgrade path to a real LLM call, grounded in the
  same analysis JSON so it can't hallucinate stats that contradict the simulation.

## Extending

- **Cirq support**: add `circuit_from_cirq_source` next to `circuit_from_qiskit_source`
  in `execution.py`, and a `cirq_circuit -> QuantumCircuit`-shaped adapter (or make
  `simulator.py`/`analyzer.py` operate on the unified `CircuitIR` in `models.py`
  instead of a raw `QuantumCircuit`, so every language shares one analysis path).
- **Circuit similarity search**: `analyzer.py`'s docstring flags exactly where this
  slots in -- it would sit alongside `detect_patterns`, likely embedding the gate
  sequence/DAG and comparing against a stored library (this is the "extensible
  architecture for future research" piece from the original brief).
- **LangChain/LangGraph**: `explainer.py` is deliberately framework-free (plain
  `httpx` calls) so there's nothing to rip out -- swap its internals for a
  LangChain agent when you want tool-calling (e.g. letting the LLM re-run
  `/api/simulate` on a modified circuit) or multi-turn memory beyond what's passed
  in `ChatRequest.messages`.
