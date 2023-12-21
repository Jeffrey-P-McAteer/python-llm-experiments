
import os
import sys
import subprocess
import shutil
import time
import traceback

python_pkgs = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.py-env')
os.makedirs(python_pkgs, exist_ok=True)
sys.path.insert(0, python_pkgs)

try:
  import environmentinator
except:
  import pip
  pip.main(f'install --target={python_pkgs} environmentinator'.split())
  import environmentinator

os.environ['OPENLLM_DO_NOT_TRACK'] = 'True'

if not 'TRANSFORMERS_CACHE' in os.environ:
    os.environ['TRANSFORMERS_CACHE'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ai_models'
    )

print(f'Using TRANSFORMERS_CACHE = {os.environ["TRANSFORMERS_CACHE"]}')
os.makedirs(os.environ['TRANSFORMERS_CACHE'], exist_ok=True)


openllm = environmentinator.ensure_module('openllm')

# Run a test query
try:
  client = openllm.client.HTTPClient('http://localhost:3000')
  print(client.query('Explain to me the difference between "further" and "farther"'))
except:
  traceback.print_exc()

  # Spawn a server for 10 minutes
  # See perf tuning env var DTYPE=float16 vs bfloat16 eg
  # See https://github.com/bentoml/OpenLLM
  subprocess.Popen([
    'timeout', '600', sys.executable, *('start facebook/opt-1.3b'.split())
  ])

  time.sleep(15)


client = openllm.client.HTTPClient('http://localhost:3000')
print(client.query('Explain to me the difference between "further" and "farther"'))


