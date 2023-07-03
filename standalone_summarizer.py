
# We begin with a ton of nice glue stuff
import os           # Removes files, makes directories, misc operating system interfaces.
import sys          # More of the same - sys.argv gives os OS arguments & sys.path is the folders python searches for libraries.
import subprocess   # Lets us spawn sub-processes
import traceback    # If we have an error, where did it happen?
import shutil       # POSIX for windorks!

# This trick allows us to install packages w/o modifying the --user site-packages
py_packages_folder = os.path.join(os.path.dirname(__file__), '.py-packages')
if not os.path.exists(py_packages_folder):
    os.makedirs(py_packages_folder, exist_ok=True)
sys.path.append(py_packages_folder)

# Tell panml/transformers where to put models b/c sometimes we want them on an external disk.
if not 'TRANSFORMERS_CACHE' in os.environ:
    preferred_transformers_cache_folders = [
      # Jeff's external USB SSD
      '/mnt/ai-models',
      # Current working directory + ai_models folder
      os.path.join(
          os.path.dirname(os.path.realpath(__file__)),
          'ai_models'
      ),
      # TODO ???
    ]
    for preferred_dir in preferred_transformers_cache_folders:
      print(f'Checking if {preferred_dir} exists...')
      if os.path.exists(preferred_dir):
        os.environ['TRANSFORMERS_CACHE'] = preferred_dir
        break
    # Otherwise pick the last one even if it does not exist
    if not 'TRANSFORMERS_CACHE' in os.environ or not os.path.exists(os.environ['TRANSFORMERS_CACHE']):
      os.environ['TRANSFORMERS_CACHE'] = preferred_transformers_cache_folders[-1]

print(f'Using TRANSFORMERS_CACHE = {os.environ["TRANSFORMERS_CACHE"]}')
os.makedirs(os.environ['TRANSFORMERS_CACHE'], exist_ok=True)


# See https://github.com/Pan-ML/panml
try:
    import panml
except:
    traceback.print_exc()
    install_cmd = [
        #sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'panml'
        sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'git+https://github.com/Pan-ML/panml.git'
    ]
    print('>>> ', ' '.join(install_cmd))
    subprocess.run(install_cmd)
    import panml

from panml.models import ModelPack


def main(args=sys.argv):

  # Self-documentings tools are nice
  if '-h' in args or '--help' in args or '/h' in args:
    print(f'''
Usage:
  {sys.executable} {args[0]}
    Prompts for input text to summarize and uses the default llm model to summarize it

  {sys.executable} {args[0]} TEXT_TO_SUMMARIZE (length > 18 chars)
    Uses the default llm model to summarize TEXT_TO_SUMMARIZE

  {sys.executable} {args[0]} MODEL_NAME
    Prompts for input text to summarize and uses the specified MODEL_NAME llm model to summarize it
    
  {sys.executable} {args[0]} MODEL_NAME TEXT_TO_SUMMARIZE
    Uses the MODEL_NAME llm model to summarize TEXT_TO_SUMMARIZE

'''.strip())
    return

  huggingface_model = 'bigscience/bloomz-7b1'
  text_to_summarize = ''

  if len(args) > 2:
    huggingface_model = args[1]
    text_to_summarize = args[2]
  elif len(args) > 1:
    if len(args[1]) < 18 and '/' in args[1]:
      huggingface_model = args[1]
    else:
      text_to_summarize = args[1]
  
  if len(text_to_summarize) < 2:
    text_to_summarize = input('Type some text to summarize: ')

  print(f'huggingface_model = {huggingface_model}')
  print(f'text_to_summarize = {text_to_summarize}')
  print(f'')

  
  lm = ModelPack(model=huggingface_model, source='huggingface', model_args={'gpu': True})

  prompt_text = text_to_summarize
  prompt_text += '\n'
  prompt_text += 'Summarize the above text.'

  lm_output = lm.predict(prompt_text, max_length=int(len(text_to_summarize) * 1.25))

  print(f'lm_output = {lm_output}')


if __name__ == '__main__':
  main()

