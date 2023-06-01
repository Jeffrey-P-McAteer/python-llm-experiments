
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
os.environ['PATH'] = os.environ['PATH']+os.pathsep+py_packages_folder

if not 'TRANSFORMERS_CACHE' in os.environ:
    os.environ['TRANSFORMERS_CACHE'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ai_models'
    )

print(f'Using TRANSFORMERS_CACHE = {os.environ["TRANSFORMERS_CACHE"]}')
os.makedirs(os.environ['TRANSFORMERS_CACHE'], exist_ok=True)



if 'transformers' in sys.argv:

  try:
      import transformers
  except:
      traceback.print_exc()
      subprocess.run([
          sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'transformers'
      ])
      import transformers
      
  try:
      import torch
  except:
      traceback.print_exc()
      subprocess.run([
          sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'torch', 'torchvision', 'torchaudio'
      ])
      import torch
    

  print('='*8, 'Transformers Library', '='*8)

  from transformers import AutoModelForCausalLM, AutoTokenizer

  tokenizer = AutoTokenizer.from_pretrained("StabilityAI/stablelm-base-alpha-3b")
  model = AutoModelForCausalLM.from_pretrained("StabilityAI/stablelm-base-alpha-3b")
  #model.half().cuda()
  #model.half()

  #inputs = tokenizer("What's your mood today?", return_tensors="pt").to("cuda")
  inputs = tokenizer("What's your mood today?", return_tensors="pt")
  tokens = model.generate(
    **inputs,
    max_new_tokens=128,
    temperature=0.7,
    do_sample=True,
  )
  print(tokenizer.decode(tokens[0], skip_special_tokens=True))


if 'llm-rs' in sys.argv or 'llmrs' in sys.argv or 'llm_rs' in sys.argv:
  print('='*8, 'LLM-RS Library', '='*8)
  
  try:
      import accelerate
  except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'accelerate'
    ])
    import accelerate
    
  # See https://huggingface.co/rustformers/bloom-ggml
  try:
      import llm_rs
  except:
      traceback.print_exc()
      subprocess.run([
          sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'llm-rs'
      ])
      import llm_rs

  from llm_rs import AutoModel, GenerationConfig

  #model = AutoModel.from_pretrained("rustformers/bloom-ggml",model_file="bloom-3b-q4_0-ggjt.bin")
  #model = AutoModel.from_pretrained("rustformers/bloom-ggml",model_file="bloom-3b-f16.bin")
  #model = AutoModel.from_pretrained("rustformers/bloom-ggml",model_file="bloom-3b-q4_0.bin")
  model = AutoModel.from_pretrained("bigscience/bloom")

  #Generate
  # print(model.generate("The meaning of life is"))

  generation_config = GenerationConfig(max_new_tokens=256)

  print(model.generate("Sally has a coworker (Jack) who doesn't help the team. Sally can encourage Jack to be a better teammate by ", generation_config))

  print(model.generate("A team of software developers goes out to lunch. John likes pizza, James likes subs, and Sally wants to eat pasta. Where should the team go for lunch?", generation_config))

  print(model.generate("The sky has grey clouds in it. What will happen next?", generation_config))





