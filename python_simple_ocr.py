
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
    import pytesseract
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'pytesseract'
    ])
    import pytesseract

if not shutil.which('tesseract'):
  print('''
Please install tesseract program.

  ubuntu: sudo apt install tesseract-ocr libtesseract-dev
  arch:   yay -S tesseract tesseract-data-eng

'''.strip())
  sys.exit(1)


# Used for OCR
try:
    import easyocr
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'easyocr'
    ])
    import easyocr

try:
    import PIL
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'Pillow'
    ])
    import PIL

# From https://stackoverflow.com/questions/42045362/change-contrast-of-image-in-pil
def change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))
    def contrast(c):
        return 128 + factor * (c - 128)
    return img.point(contrast)

def get_text(file_name):
  img_o = PIL.Image.open(file_name)
  img_o = change_contrast(img_o, 100)
  # return pytesseract.image_to_string(
  #   img_o,
  #   config='-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789/', lang='eng'
  # )
  reader = easyocr.Reader(['en'])
  return reader.readtext(file_name)



file_name = '/j/downloads/example.png'
print(f'{file_name} contents = {get_text(file_name)}')





