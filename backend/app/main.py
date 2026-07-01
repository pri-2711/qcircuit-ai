from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()  # so OPENAI_API_KEY / GEMINI_API_KEY from .env are picked up before explainer.py reads them

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import full_analysis
from .execution import CircuitParseError, build_circuit
from .explainer import chat_reply, explain_circuit
from .models import (
    AnalysisResponse,
    ChatRequest,
    ChatResponse,
    CircuitSource,
    ExplainRequest,
    ExplainResponse,
    ParseResponse,
    SimulateResponse,
)
from .simulator import circuit_to_ir, render_diagram_png_base64, simulate_statevector

app = FastAPI(
    title="Quantum Circuit Explorer & AI Tutor API",
    description="Parse, simulate, analyze, and explain quantum circuits (Qiskit / OpenQASM 2 / OpenQASM 3).",
    version="0.1.0",
)

# Wide-open CORS for local dev. Lock this down to your actual frontend origin before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_or_400(source: CircuitSource):
    try:
        return build_circuit(source.code, source.language)
    except CircuitParseError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/examples")
def examples():
    """A tiny built-in library so the frontend has something to load on first run."""
    return {
        "bell_state": {
            "language": "qiskit",
            "code": "qc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure_all()\n",
        },
        "ghz_state": {
            "language": "qiskit",
            "code": "qc = QuantumCircuit(3)\nqc.h(0)\nqc.cx(0, 1)\nqc.cx(1, 2)\nqc.measure_all()\n",
        },
        "superposition_qasm2": {
            "language": "qasm2",
            "code": (
                'OPENQASM 2.0;\ninclude "qelib1.inc";\n'
                "qreg q[1];\ncreg c[1];\nh q[0];\nmeasure q[0] -> c[0];\n"
            ),
        },
        "redundant_gates": {
            "language": "qiskit",
            "code": "qc = QuantumCircuit(2)\nqc.h(0)\nqc.h(0)\nqc.cx(0, 1)\nqc.x(1)\nqc.x(1)\n",
        },
    }


@app.post("/api/parse", response_model=ParseResponse)
def parse(source: CircuitSource):
    qc = _parse_or_400(source)
    return ParseResponse(ir=circuit_to_ir(qc), warnings=[])


@app.post("/api/simulate", response_model=SimulateResponse)
def simulate(source: CircuitSource):
    qc = _parse_or_400(source)
    sv, probs = simulate_statevector(qc)
    n = qc.num_qubits
    basis_labels = [format(i, f"0{n}b")[::-1] for i in range(len(sv.data))]
    return SimulateResponse(
        statevector_real=[float(x.real) for x in sv.data],
        statevector_imag=[float(x.imag) for x in sv.data],
        basis_labels=basis_labels,
        probabilities=probs,
        diagram_png_base64=render_diagram_png_base64(qc),
        ir=circuit_to_ir(qc),
    )


@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze(source: CircuitSource):
    qc = _parse_or_400(source)
    result = full_analysis(qc)
    return AnalysisResponse(**result)


@app.post("/api/explain", response_model=ExplainResponse)
async def explain(req: ExplainRequest):
    qc = _parse_or_400(CircuitSource(code=req.code, language=req.language))
    analysis = full_analysis(qc)
    result = await explain_circuit(analysis, req.question)
    return ExplainResponse(**result)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    analysis = None
    if req.code and req.language:
        try:
            qc = build_circuit(req.code, req.language)
            analysis = full_analysis(qc)
        except CircuitParseError:
            analysis = None  # let the chat proceed without circuit grounding rather than 400ing
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    result = await chat_reply(messages, analysis)
    return ChatResponse(**result)
