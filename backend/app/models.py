"""
Shared Pydantic schemas for the Quantum Circuit Explorer API.

Keeping every request/response shape in one place makes it much easier to
keep the frontend TypeScript-ish expectations and backend in sync as the
project grows (e.g. when Cirq support is added, we only add fields here).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field

Language = Literal["qiskit", "qasm2", "qasm3"]  # "cirq" reserved for the future


class CircuitSource(BaseModel):
    code: str = Field(..., description="Raw source code (Python/Qiskit or OpenQASM text)")
    language: Language = "qiskit"


class GateOp(BaseModel):
    name: str
    qubits: List[int]
    params: List[float] = []


class CircuitIR(BaseModel):
    """Unified intermediate representation used across the whole pipeline."""
    num_qubits: int
    num_clbits: int
    operations: List[GateOp]
    qasm2: Optional[str] = None


class ParseResponse(BaseModel):
    ir: CircuitIR
    warnings: List[str] = []


class SimulateResponse(BaseModel):
    statevector_real: List[float]
    statevector_imag: List[float]
    basis_labels: List[str]
    probabilities: Dict[str, float]
    diagram_png_base64: str
    ir: CircuitIR


class AnalysisResponse(BaseModel):
    num_qubits: int
    depth: int
    gate_counts: Dict[str, int]
    total_gates: int
    two_qubit_gate_count: int
    entangled: bool
    entanglement_entropy_per_qubit: Dict[str, float]
    detected_patterns: List[Dict[str, Any]]
    optimization_hints: List[str]


class ExplainRequest(BaseModel):
    code: str
    language: Language = "qiskit"
    question: Optional[str] = None


class ExplainResponse(BaseModel):
    explanation: str
    source: Literal["llm", "template"]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    code: Optional[str] = None
    language: Optional[Language] = None


class ChatResponse(BaseModel):
    reply: str
    source: Literal["llm", "template"]


class ErrorResponse(BaseModel):
    detail: str
