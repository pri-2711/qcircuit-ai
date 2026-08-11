import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path('.').resolve()))
import app.explainer as explainer

print('ENV_FILE_EXISTS', Path('.env').exists())
print('KEY_LOADED', bool(explainer._get_api_keys()[1]))
print('KEY_PREFIX', (explainer._get_api_keys()[1] or '')[:8])

async def main():
    result = await explainer.explain_circuit({}, 'What is a vector?', None, None)
    print('SOURCE', result['source'])
    print('EXPLANATION', result['explanation'][:800])

asyncio.run(main())
