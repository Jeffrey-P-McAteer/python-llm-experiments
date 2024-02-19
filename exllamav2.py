

import os, sys
import traceback

import code, subprocess, traceback
runner_env = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'runner_env'
)
os.makedirs(runner_env, exist_ok=True)
print('Putting python libs in ', runner_env)
sys.path.append(runner_env)
os.environ['PYTHONPATH'] = runner_env+os.pathsep+os.environ.get('PYTHONPATH', '')


try:
    import torch
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={runner_env}', 'torch', 'torchvision', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cu118'
    ])
    import torch

exllamav2_dir = f'{runner_env}/exllamav2'
if not os.path.exists(exllamav2_dir):
  subprocess.run('git clone https://github.com/turboderp/exllamav2'.split() + [exllamav2_dir], check=True)
  subprocess.run(f'python -m pip install --target={runner_env} .'.split(), check=True, cwd=exllamav2_dir)

sys.path.append(exllamav2_dir)
os.environ['PYTHONPATH'] = exllamav2_dir+os.pathsep+os.environ.get('PYTHONPATH', '')


model_file = 'transformers_cache/Orion-14B-exl2_3.0bpw_output.safetensors'
if not os.path.exists(model_file):
  os.makedirs(os.path.dirname(model_file), exist_ok=True)
  subprocess.run([
    'curl', '--output', model_file, 'https://huggingface.co/turboderp/Orion-14B-exl2/resolve/3.0bpw/output.safetensors?download=true'
  ])


# From https://github.com/turboderp/exllamav2/blob/master/test_inference.py

from exllamav2 import(
    ExLlamaV2,
    ExLlamaV2Config,
    ExLlamaV2Cache,
    ExLlamaV2Cache_8bit,
    ExLlamaV2Tokenizer,
    model_init,
)

from exllamav2.generator import (
    ExLlamaV2BaseGenerator,
    ExLlamaV2Sampler
)

from exllamav2.attn import ExLlamaV2Attention
from exllamav2.mlp import ExLlamaV2MLP
from exllamav2.moe_mlp import ExLlamaV2MoEMLP

import argparse, os, math, time
import torch
import torch.nn.functional as F
from conversion.tokenize import get_tokens
from conversion.quantize import list_live_tensors
import gc

# from exllamav2.mlp import set_catch

import sys
import json

torch.cuda._lazy_init()
torch.set_printoptions(precision = 10)


