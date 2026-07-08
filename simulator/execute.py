import builtins
from typing import Any, Dict, Optional

from qiskit import QuantumCircuit

from utils.errors import format_execution_error


def execute_user_code(code: str) -> Dict[str, Any]:
    namespace = {"__builtins__": builtins}

    try:
        exec(code, namespace)
    except Exception as error:  # pragma: no cover - exercised at runtime
        return {"success": False, "circuit": None, "error": format_execution_error(error)}

    circuit = _find_quantum_circuit(namespace)
    if circuit is None:
        return {
            "success": False,
            "circuit": None,
            "error": "No QuantumCircuit object was created. Define a circuit variable such as 'qc = QuantumCircuit(1)'.",
        }

    return {"success": True, "circuit": circuit, "error": None}


def _find_quantum_circuit(namespace: Dict[str, Any]) -> Optional[QuantumCircuit]:
    for value in namespace.values():
        if isinstance(value, QuantumCircuit):
            return value
    return None
