
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

# Used for OCR
try:
    import easyocr
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'easyocr'
    ])
    import easyocr

def get_text(file_name):
  reader = easyocr.Reader(['en'])
  torch_result_dict = reader.readtext(file_name)
  return [text for bbox, text, confidence in torch_result_dict]



file_name = '/j/downloads/example.png'
print(f'{file_name} contents = {get_text(file_name)}')





