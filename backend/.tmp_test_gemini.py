import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
from app.explainer import explain_circuit, _get_api_keys

print('KEY_LOADED', bool(_get_api_keys()[1]))

result = asyncio.run(explain_circuit({}, 'What is a vector?', None, None))
print('SOURCE', result['source'])
print('EXPLANATION', result['explanation'][:500])
