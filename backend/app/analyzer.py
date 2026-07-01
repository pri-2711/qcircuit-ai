"""
Static + state-based analysis of a QuantumCircuit.

Pattern detection is intentionally split into two strategies, because each
catches different things:

  1. STATE-BASED: look at the resulting statevector's structure (e.g. "two
     equal-magnitude basis states that are bit-flips of each other" = Bell
     pair). Robust to *how* the state was built, but only works for
     patterns with a recognizable state signature.

  2. STRUCTURE-BASED: look at gate names/topology (e.g. a block literally
     named "QFT", or a repeating H-layer + oracle + diffuser motif for
     Grover). Needed for patterns like Grover's algorithm where the state
     itself doesn't have a fixed signature (it depends on the oracle).

This is explicitly a heuristic v1. The natural extension mentioned in the
project brief -- circuit similarity search against a library of known
circuits (e.g. via gate-sequence embeddings or graph isomorphism on the DAG)
-- would replace/augment this file, not `simulator.py` or `execution.py`.
"""
from __future__ import annotations

import cmath
from typing import Any, Dict, List

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, partial_trace, entropy

from .simulator import strip_measurements


def basic_stats(qc: QuantumCircuit) -> Dict[str, Any]:
    gate_counts = dict(qc.count_ops())
    two_qubit_gates = {"cx", "cz", "cy", "swap", "ch", "crz", "cry", "crx", "cp", "rzz", "rxx", "ryy"}
    two_qubit_count = sum(v for k, v in gate_counts.items() if k in two_qubit_gates)
    total_gates = sum(v for k, v in gate_counts.items() if k not in ("barrier", "measure"))
    return {
        "num_qubits": qc.num_qubits,
        "depth": qc.depth(),
        "gate_counts": gate_counts,
        "total_gates": total_gates,
        "two_qubit_gate_count": two_qubit_count,
    }


def entanglement_report(sv: Statevector, num_qubits: int) -> Dict[str, Any]:
    """Per-qubit entanglement entropy of the reduced state (in bits).

    ~0 => that qubit is in a pure/unentangled state relative to the rest.
    >0 => entangled with the rest of the register (max 1.0 for a single
    qubit reduced state).
    """
    per_qubit: Dict[str, float] = {}
    any_entangled = False
    for q in range(num_qubits):
        others = [i for i in range(num_qubits) if i != q]
        rho = partial_trace(sv, others) if others else sv
        e = float(entropy(rho, base=2)) if others else 0.0
        e = 0.0 if e < 1e-6 else round(e, 4)
        per_qubit[str(q)] = e
        if e > 1e-6:
            any_entangled = True
    return {"entangled": any_entangled, "entanglement_entropy_per_qubit": per_qubit}


def _state_signature(sv: Statevector, tol: float = 1e-6):
    """Returns [(bitstring, amplitude), ...] for basis states with non-negligible amplitude."""
    n = sv.num_qubits
    out = []
    for i, amp in enumerate(sv.data):
        if abs(amp) > tol:
            out.append((format(i, f"0{n}b")[::-1], amp))  # qiskit little-endian -> human-readable
    return out


def detect_bell_and_ghz(sv: Statevector) -> List[Dict[str, Any]]:
    found = []
    sig = _state_signature(sv)
    n = sv.num_qubits

    if n == 2 and len(sig) == 2:
        (b0, a0), (b1, a1) = sig
        equal_mag = abs(abs(a0) - abs(a1)) < 1e-6 and abs(abs(a0) - 0.70710678) < 1e-3
        bit_flip_pair = all(x != y for x, y in zip(b0, b1))
        if equal_mag and bit_flip_pair:
            phase = cmath.phase(a1 / a0)
            kind = "Phi+" if abs(phase) < 1e-3 else (
                "Phi-" if abs(abs(phase) - np.pi) < 1e-3 else "Psi+/Psi-"
            )
            found.append({
                "name": "Bell state",
                "confidence": 0.95,
                "detail": f"Maximally entangled 2-qubit state (variant: {kind}). "
                          "Classic building block for teleportation, superdense coding, "
                          "and as the simplest example of entanglement.",
            })

    if n >= 3 and len(sig) == 2:
        (b0, a0), (b1, a1) = sig
        all_zero = set(b0) == {"0"}
        all_one = set(b1) == {"1"}
        equal_mag = abs(abs(a0) - abs(a1)) < 1e-6
        if all_zero and all_one and equal_mag:
            found.append({
                "name": "GHZ state",
                "confidence": 0.95,
                "detail": f"{n}-qubit Greenberger-Horne-Zeilinger state: an equal "
                          "superposition of all-0 and all-1. Maximally entangled "
                          "across all qubits and famously fragile to single-qubit noise.",
            })

    if n >= 2 and len(sig) == 2 ** n:
        mags = sorted(abs(a) for _, a in sig)
        if abs(mags[0] - mags[-1]) < 1e-6:
            found.append({
                "name": "Uniform superposition",
                "confidence": 0.6,
                "detail": "All basis states are equally likely (flat distribution). "
                          "Typical of an all-H initialization layer, e.g. the first "
                          "step of Grover's algorithm or QFT applied to |0...0>.",
            })
    return found


def detect_structural_patterns(qc: QuantumCircuit, gate_counts: Dict[str, int]) -> List[Dict[str, Any]]:
    found = []
    names = set(gate_counts.keys())
    lower_names = {n.lower() for n in names}

    if any("qft" in n for n in lower_names):
        found.append({
            "name": "Quantum Fourier Transform",
            "confidence": 0.9,
            "detail": "A named QFT block was found. QFT is the quantum analogue of the "
                      "discrete Fourier transform and the core subroutine of phase "
                      "estimation, Shor's algorithm, and many arithmetic circuits.",
        })

    if any(n in lower_names for n in ("diffuser", "grover_operator", "oracle")):
        found.append({
            "name": "Grover's algorithm",
            "confidence": 0.8,
            "detail": "Named oracle/diffuser blocks were found, matching Grover's "
                      "amplitude-amplification structure.",
        })
    elif "h" in names and any(n.startswith("mc") or n in ("ccx", "ccz") for n in lower_names):
        h_layers = sum(1 for instr in qc.data if instr.operation.name == "h")
        if h_layers >= 2 * qc.num_qubits:
            found.append({
                "name": "Grover's algorithm (heuristic)",
                "confidence": 0.5,
                "detail": "Repeated Hadamard layers plus multi-controlled gates suggest "
                          "a Grover-style oracle + diffusion pattern, but this is a weak "
                          "structural guess rather than a confirmed match.",
            })

    rotation_gates = {"rx", "ry", "rz"}
    entangling_gates = {"cx", "cz", "crz", "cry", "crx"}
    if lower_names & rotation_gates and lower_names & entangling_gates:
        rot_count = sum(v for k, v in gate_counts.items() if k in rotation_gates)
        ent_count = sum(v for k, v in gate_counts.items() if k in entangling_gates)
        if rot_count >= qc.num_qubits and ent_count >= 1 and rot_count >= ent_count:
            found.append({
                "name": "Variational ansatz (heuristic)",
                "confidence": 0.4,
                "detail": "Alternating parameterized rotations and entangling gates "
                          "resemble a hardware-efficient ansatz, as used in VQE/QAOA. "
                          "Structural guess only -- confirm by checking if angles are "
                          "meant to be optimized.",
            })

    return found


def detect_patterns(qc: QuantumCircuit, sv: Statevector, gate_counts: Dict[str, int]) -> List[Dict[str, Any]]:
    return detect_bell_and_ghz(sv) + detect_structural_patterns(qc, gate_counts)


def optimization_hints(qc: QuantumCircuit) -> List[str]:
    hints: List[str] = []
    try:
        optimized = transpile(qc, optimization_level=3)
        if optimized.depth() < qc.depth():
            hints.append(
                f"Transpiling with optimization_level=3 reduces circuit depth from "
                f"{qc.depth()} to {optimized.depth()} (gate cancellation/merging). "
                "Consider running your circuit through qiskit.transpile before execution."
            )
        before_2q = sum(v for k, v in qc.count_ops().items() if k in {"cx", "cz", "swap"})
        after_2q = sum(v for k, v in optimized.count_ops().items() if k in {"cx", "cz", "swap"})
        if after_2q < before_2q:
            hints.append(
                f"Two-qubit gate count can drop from {before_2q} to {after_2q} after "
                "optimization -- meaningful on real hardware, where 2-qubit gates "
                "dominate error rates."
            )
    except Exception:
        pass

    # cheap structural hints that don't need transpile
    ops = [ (instr.operation.name, tuple(qc.find_bit(q).index for q in instr.qubits))
            for instr in qc.data if instr.operation.name not in ("barrier", "measure") ]
    for i in range(len(ops) - 1):
        name_a, qubits_a = ops[i]
        name_b, qubits_b = ops[i + 1]
        if name_a == name_b and qubits_a == qubits_b and name_a in {"h", "x", "y", "z", "cx", "cz", "swap"}:
            hints.append(
                f"Adjacent identical self-inverse gates found: two consecutive "
                f"'{name_a}' on qubit(s) {qubits_a} cancel out and can likely be removed."
            )
            break  # one example is enough noise for the tutor UI

    if not hints:
        hints.append("No obvious redundancy found -- this circuit already looks fairly tight.")
    return hints


def full_analysis(qc: QuantumCircuit) -> Dict[str, Any]:
    stats = basic_stats(qc)
    unitary_only = strip_measurements(qc)
    sv = Statevector.from_instruction(unitary_only)
    ent = entanglement_report(sv, qc.num_qubits)
    patterns = detect_patterns(qc, sv, stats["gate_counts"])
    hints = optimization_hints(qc)

    return {
        **stats,
        **ent,
        "detected_patterns": patterns,
        "optimization_hints": hints,
    }
