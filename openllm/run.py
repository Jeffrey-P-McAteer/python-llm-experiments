
import os
import sys
import subprocess
import shutil
import time
import traceback
import asyncio

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
os.environ['PYTHONPATH'] = python_pkgs + ':' + os.path.join(python_pkgs, '3_11') + ':' + os.environ.get('PYTHONPATH', '')

print(f'Using PYTHONPATH = {os.environ["PYTHONPATH"]}')

if not 'TRANSFORMERS_CACHE' in os.environ:
    os.environ['TRANSFORMERS_CACHE'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ai_models'
    )

print(f'Using TRANSFORMERS_CACHE = {os.environ["TRANSFORMERS_CACHE"]}')
os.makedirs(os.environ['TRANSFORMERS_CACHE'], exist_ok=True)

if not 'HF_HOME' in os.environ:
    os.environ['HF_HOME'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ai_models'
    )

print(f'Using HF_HOME = {os.environ["HF_HOME"]}')
os.makedirs(os.environ['HF_HOME'], exist_ok=True)

if not 'HF_TOKEN' in os.environ:
  print('Please login to HF and generate a token at https://huggingface.co/settings/tokens')
  print('Then assign to HF_TOKEN= and re-launch.')
  sys.exit(5)

hf_token = os.environ['HF_TOKEN']


openllm = environmentinator.ensure_module('openllm', 'openllm[vllm]')
langchain = environmentinator.ensure_module('langchain')
llama_index = environmentinator.ensure_module('llama_index')




async def main(args=sys.argv):

  try:
    llm = openllm.LLM('facebook/opt-2.7b', backend='vllm')
    print(await llm.generate('What is the meaning of life?'))
  except:
    traceback.print_exc()



  # try:
  #   from llama_index.llms.openllm import OpenLLM
  #   llm = OpenLLM('HuggingFaceH4/zephyr-7b-alpha')
  #   print(llm.complete('The meaning of life is'))
  # except:
  #   traceback.print_exc()


  # try:
  #   from langchain.llms import OpenLLM
  #   llm = OpenLLM(model_name='llama', model_id='meta-llama/Llama-2-7b-hf', token=hf_token)
  #   print(llm('What is the difference between a duck and a goose? And why there are so many Goose in Canada?'))
  # except:
  #   traceback.print_exc()





if __name__ == '__main__':
  asyncio.run(main())


