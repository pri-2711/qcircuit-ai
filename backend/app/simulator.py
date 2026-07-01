"""
Ideal (noiseless) statevector simulation.

We deliberately use `qiskit.quantum_info.Statevector` rather than
`qiskit-aer` for the MVP: it needs no extra C++ backend, it's exact, and it
is more than enough for the qubit counts a tutoring tool should realistically
render (diagrams/statevectors stop being readable well before 10 qubits
anyway). Swap in Aer later if you add noise models or need faster large
simulations.
"""
from __future__ import annotations

import base64
import io
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")  # headless rendering - required on a server

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from .models import CircuitIR, GateOp


def strip_measurements(qc: QuantumCircuit) -> QuantumCircuit:
    """Statevector sim requires a purely unitary circuit; drop measure/barrier/reset."""
    clean = QuantumCircuit(qc.num_qubits)
    for instruction in qc.data:
        if instruction.operation.name in ("measure", "barrier", "reset"):
            continue
        clean.append(instruction.operation, instruction.qubits, instruction.clbits)
    return clean


def circuit_to_ir(qc: QuantumCircuit) -> CircuitIR:
    ops: List[GateOp] = []
    for instruction in qc.data:
        op = instruction.operation
        qubit_indices = [qc.find_bit(q).index for q in instruction.qubits]
        params = [float(p) for p in op.params if isinstance(p, (int, float))]
        ops.append(GateOp(name=op.name, qubits=qubit_indices, params=params))

    try:
        from qiskit import qasm2
        qasm_text = qasm2.dumps(qc)
    except Exception:
        qasm_text = None

    return CircuitIR(
        num_qubits=qc.num_qubits,
        num_clbits=qc.num_clbits,
        operations=ops,
        qasm2=qasm_text,
    )


def simulate_statevector(qc: QuantumCircuit) -> Tuple[Statevector, Dict[str, float]]:
    unitary_only = strip_measurements(qc)
    sv = Statevector.from_instruction(unitary_only)
    raw_probs = sv.probabilities_dict()
    # numpy scalar keys/values -> plain python for clean JSON
    probs = {str(k): float(v) for k, v in raw_probs.items() if v > 1e-10}
    return sv, probs


def render_diagram_png_base64(qc: QuantumCircuit) -> str:
    fig = qc.draw("mpl", style={"backgroundcolor": "#FFFFFF"})
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=140)
    try:
        import matplotlib.pyplot as plt
        plt.close(fig)
    except Exception:
        pass
    return base64.b64encode(buf.getvalue()).decode("ascii")
