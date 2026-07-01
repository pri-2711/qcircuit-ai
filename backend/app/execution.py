"""
Source -> QuantumCircuit.

Two input languages are supported today:
  - "qiskit": raw Python that builds a `QuantumCircuit` (e.g. pasted from a notebook)
  - "qasm2" / "qasm3": OpenQASM text

SECURITY NOTE
-------------
Running arbitrary user-submitted Python (the "qiskit" language path) is the
same class of feature as a Jupyter notebook or the IBM Quantum Composer: it
is *supposed* to execute code. That is inherently risky for a public,
multi-tenant deployment. This module applies a best-effort restriction
(limited builtins, whitelisted imports, wall-clock timeout) which is enough
for trusted local/dev use, but it is NOT a real security boundary.

Before deploying this behind a public URL, run circuit execution inside a
disposable, network-isolated container/microVM (e.g. gVisor, Firecracker,
or a locked-down Docker container with --network=none, a CPU/memory limit,
and a non-root user) and treat the API-level restrictions here as a second
layer of defense, not the only one.
"""
from __future__ import annotations

import builtins as _builtins
import multiprocessing as mp
import platform
from typing import Any, Dict

from qiskit import QuantumCircuit, qasm2, qasm3


class CircuitParseError(Exception):
    pass


# `fork` lets the child reuse the already-imported qiskit/numpy from the
# parent (spawning fresh interpreters and re-importing qiskit costs ~1-2s
# per request, which would make every circuit run feel sluggish). `fork`
# is POSIX-only, so Windows dev machines fall back to `spawn` automatically.
_MP_CONTEXT = mp.get_context("fork") if platform.system() != "Windows" else mp.get_context("spawn")


# Only these top-level names are reachable from user code. This blocks file
# I/O, network access, subprocess, and arbitrary imports outside the
# quantum-computing stack.
_SAFE_BUILTINS_WHITELIST = {
    "range", "len", "enumerate", "list", "dict", "set", "tuple", "zip",
    "map", "filter", "sum", "min", "max", "abs", "round", "float", "int",
    "str", "bool", "print", "isinstance", "type", "reversed", "sorted",
    "pow", "divmod", "complex", "True", "False", "None",
}


def _restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    allowed_prefixes = ("qiskit", "numpy", "math", "cmath")
    if not any(name == p or name.startswith(p + ".") for p in allowed_prefixes):
        raise ImportError(
            f"Import of '{name}' is not permitted in the circuit sandbox. "
            "Only qiskit / numpy / math / cmath are available."
        )
    return _builtins.__import__(name, globals, locals, fromlist, level)


def _build_sandbox_globals() -> Dict[str, Any]:
    import numpy  # noqa: F401
    import math  # noqa: F401
    import qiskit  # noqa: F401
    from qiskit import QuantumCircuit as _QC  # re-exported for convenience
    from qiskit.circuit import QuantumRegister, ClassicalRegister  # noqa: F401

    safe_builtins = {k: getattr(_builtins, k) for k in _SAFE_BUILTINS_WHITELIST if hasattr(_builtins, k)}
    safe_builtins["__import__"] = _restricted_import

    return {
        "__builtins__": safe_builtins,
        "qiskit": qiskit,
        "QuantumCircuit": _QC,
        "QuantumRegister": QuantumRegister,
        "ClassicalRegister": ClassicalRegister,
        "numpy": numpy,
        "np": numpy,
        "math": math,
    }


def _resolve_circuit(sandbox: Dict[str, Any], local_ns: Dict[str, Any]) -> QuantumCircuit:
    namespace = {**sandbox, **local_ns}
    for key in ("qc", "circuit"):
        candidate = namespace.get(key)
        if isinstance(candidate, QuantumCircuit):
            return candidate

    circuits = [v for v in local_ns.values() if isinstance(v, QuantumCircuit)]
    if circuits:
        return circuits[-1]

    raise CircuitParseError(
        "No QuantumCircuit was found. Assign your circuit to a variable "
        "named `qc` (e.g. `qc = QuantumCircuit(2)`)."
    )


def _worker_entrypoint(code: str, result_queue: "mp.Queue") -> None:
    """Runs in a forked child process -- crashing/hanging here can't take down the API server."""
    try:
        sandbox = _build_sandbox_globals()
        local_ns: Dict[str, Any] = {}
        exec(compile(code, "<user_circuit>", "exec"), sandbox, local_ns)
        qc = _resolve_circuit(sandbox, local_ns)
        result_queue.put(("ok", qc))
    except SyntaxError as e:
        result_queue.put(("error", f"Syntax error in submitted code: {e}"))
    except CircuitParseError as e:
        result_queue.put(("error", str(e)))
    except Exception as e:  # noqa: BLE001 - surface the user's own error to them
        result_queue.put(("error", f"{type(e).__name__}: {e}"))


def circuit_from_qiskit_source(code: str, timeout_seconds: int = 5) -> QuantumCircuit:
    """Executes user Python in a forked subprocess with a wall-clock timeout.

    Running in a subprocess (rather than in-process with a signal-based
    alarm) buys two things: the timeout works no matter which thread FastAPI
    happens to run this on, and a crash/hang/fork-bomb in user code can't
    take the API server down with it.
    """
    result_queue: mp.Queue = _MP_CONTEXT.Queue()
    process = _MP_CONTEXT.Process(target=_worker_entrypoint, args=(code, result_queue))
    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join(1)
        if process.is_alive():
            process.kill()
        raise CircuitParseError(f"Execution exceeded {timeout_seconds}s time limit")

    if result_queue.empty():
        raise CircuitParseError(
            f"Circuit execution crashed unexpectedly (exit code {process.exitcode})"
        )

    status, payload = result_queue.get()
    if status == "error":
        raise CircuitParseError(f"Error while running circuit code: {payload}")
    return payload


def circuit_from_qasm(code: str, language: str) -> QuantumCircuit:
    try:
        if language == "qasm2":
            return qasm2.loads(code)
        if language == "qasm3":
            return qasm3.loads(code)
    except Exception as e:  # noqa: BLE001
        raise CircuitParseError(f"Failed to parse {language.upper()}: {e}")
    raise CircuitParseError(f"Unknown QASM dialect: {language}")


def build_circuit(code: str, language: str) -> QuantumCircuit:
    if language == "qiskit":
        return circuit_from_qiskit_source(code)
    if language in ("qasm2", "qasm3"):
        return circuit_from_qasm(code, language)
    raise CircuitParseError(f"Unsupported language: {language}")
