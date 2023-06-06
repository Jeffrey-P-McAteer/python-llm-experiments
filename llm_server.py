
# Given a model source, model name, and folder,
# Loads the model and polls folder for "predict.*.txt" files.
# Reads input of .txt file and writes output to "response.*.txt"


import os
import sys
import subprocess
import traceback
import shutil
import time
import random

# This trick allows us to install packages w/o modifying the --user site-packages
py_packages_folder = os.path.join(os.path.dirname(__file__), '.py-packages')
if not os.path.exists(py_packages_folder):
    os.makedirs(py_packages_folder, exist_ok=True)
sys.path.append(py_packages_folder)


if not 'TRANSFORMERS_CACHE' in os.environ:
    os.environ['TRANSFORMERS_CACHE'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ai_models'
    )

print(f'Using TRANSFORMERS_CACHE = {os.environ["TRANSFORMERS_CACHE"]}')
os.makedirs(os.environ['TRANSFORMERS_CACHE'], exist_ok=True)

DEBUG = False
if 'DEBUG' in os.environ:
    DEBUG = bool(os.environ['DEBUG'])

print(f'DEBUG = {DEBUG}')


# See https://github.com/Pan-ML/panml
try:
    import panml
except:
    traceback.print_exc()
    subprocess.run([
        #sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'panml'
        sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'git+https://github.com/Pan-ML/panml.git'
    ])
    import panml

from panml.models import ModelPack

MAX_GAME_TOKENS = int(os.environ.get('MAX_GAME_TOKENS', '12500'))
print(f'MAX_GAME_TOKENS = {MAX_GAME_TOKENS}')

model_source = sys.argv[1].strip()
model_to_use = sys.argv[2].strip()
llm_server_folder = sys.argv[3].strip()

print(f'model_source={model_source}')
print(f'model_to_use={model_to_use}')
print(f'llm_server_folder={llm_server_folder}')

lm = ModelPack(model=model_to_use, source=model_source, model_args={'gpu': True})


while True:
  try:
    time.sleep(0.1)

    for filename in os.listdir(llm_server_folder):
      if 'server-live-check.txt' in filename:
        while os.path.exists( os.path.join(llm_server_folder, filename) ):
          time.sleep(0.1)
          try:
             os.remove( os.path.join(llm_server_folder, filename) )
             break
          except:
             pass
        print('Server is alive!')

      elif 'predict.txt' in filename:
        prompt_text = ''
        with open(os.path.join(llm_server_folder, filename), 'r') as fd:
          prompt_text = fd.read()
          if not isinstance(prompt_text, str):
            prompt_text = prompt_text.decode('utf-8')

        lm_output = lm.predict(prompt_text, max_length=MAX_GAME_TOKENS)

        with open(os.path.join(llm_server_folder, 'response.txt'), 'w') as fd:
          fd.write(lm_output['text'])

        print()
        for prompt_line in prompt_text.splitlines():
          print(f'< {prompt_line}')
        for response_line in lm_output["text"].splitlines():
          print(f'> {response_line}')
        print()

        while os.path.exists( os.path.join(llm_server_folder, filename) ):
           time.sleep(0.1)
           try:
              os.remove( os.path.join(llm_server_folder, filename) )
              break
           except:
              pass

  except:
    traceback.print_exc()
    time.sleep(1)




