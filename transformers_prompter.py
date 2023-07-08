import os, sys
import traceback


os.environ['TRANSFORMERS_CACHE'] = os.environ.get('TRANSFORMERS_CACHE', os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'transformers_cache'
))
os.makedirs(os.environ['TRANSFORMERS_CACHE'], exist_ok=True)
print('Saving models in', os.environ['TRANSFORMERS_CACHE'])

import code, subprocess, traceback
runner_env = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'runner_env'
)
os.makedirs(runner_env, exist_ok=True)
print('Putting python libs in ', runner_env)
sys.path.append(runner_env)


try:
    import torch
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={runner_env}', 'torch', 'torchvision', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cu118'
    ])
    import torch


try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={runner_env}', 'transformers[torch]'
    ])
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

try:
    import xformers
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={runner_env}', 'xformers'
    ])
    import xformers


# model_name = 'bigscience/bloom'
# model_name = 'gpt2'
model_name = 'lmsys/longchat-13b-16k'

print(f'Loading model {model_name}')

cuda_dev_num = 0
print(f'Using CUDA device: {torch.cuda.get_device_name(cuda_dev_num)}')
print(f'num_workers = {os.cpu_count()}')

generator = pipeline(
        model=model_name,
        num_workers=os.cpu_count(),
        device=cuda_dev_num
)

try:
    print(f'generator = {generator}')
    print(f'{generator("Hello user, my name is", max_new_tokens=200)}')
except:
    traceback.print_exc()

print('''
# 
# Run text generation like:
#     generator('Hello, my name is', max_new_tokens=200)
# 
# Args for generator's __call__ are documented at https://huggingface.co/docs/transformers/main/en/main_classes/pipelines#transformers.TextGenerationPipeline.__call__
#
#
'''.strip())

vars = globals()
vars.update(locals())
code.interact(local=vars)

