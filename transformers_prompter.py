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
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={runner_env}', 'transformers[torch]'
    ])
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

try:
    import torch
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={runner_env}', 'torch', 'torchvision', 'torchaudio', '--index-url https://download.pytorch.org/whl/cu118'
    ])
    import torch


# model_name = 'bigscience/bloom'
model_name = 'gpt2'

print(f'Loading model {model_name}')

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map='auto',
    torch_dtype='auto'
)

try:
    print(f'tokenizer = {tokenizer}')
    print(f'model = {model}')
    cuda_dev_num = 0
    print(f'Using CUDA device: {torch.cuda.get_device_name(cuda_dev_num)}')
    generator = pipeline(
            model=model,
            tokenizer=tokenizer,
            num_workers=24,
            device=torch.cuda.device(cuda_dev_num)
    )
    print(f'generator = {generator}')
    print(f'{generator("Hello user, my name is", do_sample=False)}')
except:
    traceback.print_exc()

vars = globals()
vars.update(locals())
code.interact(local=vars)

