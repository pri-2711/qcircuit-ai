import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
import app.explainer as explainer

analysis = {
    'num_qubits': 2,
    'depth': 2,
    'total_gates': 2,
    'gate_counts': {'h': 1, 'cx': 1},
    'entangled': True,
    'entanglement_entropy_per_qubit': {'q0': 0.7, 'q1': 0.7},
    'detected_patterns': [{'name': 'Bell state', 'confidence': 0.95, 'detail': 'Bell pair pattern'}],
    'optimization_hints': ['use fewer gates'],
}

async def main():
    result = await explainer.explain_circuit(analysis, 'What is a vector?', 'qc = QuantumCircuit(2)', 'qiskit')
    Path('gemini_check.json').write_text(json.dumps({
        'key_loaded': bool(explainer._get_api_keys()[1]),
        'source': result['source'],
        'explanation': result['explanation'][:1500],
    }, ensure_ascii=False), encoding='utf-8')

asyncio.run(main())
