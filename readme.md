
# Managing the Monsters

_a workplace chaos game_

Running

```bash
# Set PYTHON_BIN_DIR in shell.bat
.\shell.bat

python managing_the_monsters.py [optional game nonce to re-play old games]


systemd-run --scope -p MemoryHigh=12G -p MemorySwapMax=999G  --user python managing_the_monsters.py

/usr/bin/python /j/proj/python-llm-experiments/llm_server.py huggingface google/flan-t5-xl /j/proj/python-llm-experiments/llm-server-folder

systemd-run --scope -p MemoryHigh=12G -p MemorySwapMax=999G -p Nice=2 --user python llm_server.py huggingface google/flan-t5-xl /j/proj/python-llm-experiments/llm-server-folder


systemd-run --scope -p MemoryHigh=12G -p MemorySwapMax=999G -p Nice=2 --user python llm_server.py huggingface google/flan-t5-large /j/proj/python-llm-experiments/llm-server-folder


```

## Example games

```
python managing_the_monsters.py 1685027779
Using TRANSFORMERS_CACHE = \\jcce.jwac.mil\CMDShare\Users\jmcateer\python-llm-experiments\ai_models
[nltk_data] Downloading package vader_lexicon to
[nltk_data]     \\jcce.jwac.mil\CMDShare\Users\jmcateer\python-llm-
[nltk_data]     experiments\ai_models...
[nltk_data]   Package vader_lexicon is already up-to-date!
game_seed = 1685027779
Remember the game seed if you want to play the same game again by passing it as Arg1!
MAX_GAME_TOKENS = 12500


You are a manager and two employees with a problem have come into your office.
Talk them through their problem until both employees are happy.

Mark Miller is a 30-year-old male. Mark is the Applications developer around here.

Christopher Foley is a 20-year-old male. Christopher is our Garment/textile technologist around here.

Mark has ruined Christopher's project!


Loading google/flan-t5-xl from huggingface

Model processing is set on CPU
Loading checkpoint shards: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [03:40<00:00, 110.38s/it]
===== Scores =====
Mark Miller feels He is a bad person. ({'neg': 0.538, 'neu': 0.462, 'pos': 0.0, 'compound': -0.5423})
Christopher Foley feels He is angry. ({'neg': 0.623, 'neu': 0.377, 'pos': 0.0, 'compound': -0.5106})
==================
Manager>
Manager> Christopher, your project will be fixed by myself and Mark. Mark will be happy to help, right Mark?
Mark: Yes, I will.
Christopher: Christopher is grateful.
===== Scores =====
Mark Miller feels He is happy to help. ({'neg': 0.0, 'neu': 0.319, 'pos': 0.681, 'compound': 0.7506})
Christopher Foley feels grateful ({'neg': 0.0, 'neu': 0.0, 'pos': 1.0, 'compound': 0.4588})
==================

Success! You took 2.0 steps to solve Mark Miller and Christopher Foley's problem!

Goodbye!
```


```
NOAUTOSPAWN=1 python managing_the_monsters.py 1685573583
Using TRANSFORMERS_CACHE = /j/proj/python-llm-experiments/ai_models
DEBUG = False
[nltk_data] Downloading package vader_lexicon to /j/proj/python-llm-
[nltk_data]     experiments/ai_models...
[nltk_data]   Package vader_lexicon is already up-to-date!
NOAUTOSPAWN in environ, continuing w/o checking if server process is running!
game_seed = 1685573583
Remember the game seed if you want to play the same game again by passing it as Arg1!
MAX_GAME_TOKENS = 12500


You are a manager and two employees with a problem have come into your office.
Talk them through their problem until both employees are happy.

Jessica Santiago is a 65-year-old female. Jessica is the Medical technical officer around here.

Rebecca Simmons is a 43-year-old female. Rebecca is our Data processing manager around here.

Jessica is putting day-old pizza boxes in the trash and not taking the trash out. Rebecca ends up always doing the work!

===== Scores =====
Jessica Santiago feels She is lazy.  ({'neg': 0.556, 'neu': 0.444, 'pos': 0.0, 'compound': -0.3612})
Rebecca Simmons feels (ii).  ({'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0})
==================
Manager> Jessica, please take out the trash next time you eat pizza. It will make Rebecca's life a lot easier!
Rebecca:
===== Scores =====
Jessica Santiago feels Jessica feels bad about not taking out the trash.  ({'neg': 0.304, 'neu': 0.696, 'pos': 0.0, 'compound': -0.5423})
Rebecca Simmons feels Rebecca feels annoyed.  ({'neg': 0.565, 'neu': 0.435, 'pos': 0.0, 'compound': -0.3818})
==================
Manager> Jessica I know you can do this! Rebecca you should be happy Jessica will be helping out!
Rebecca:
===== Scores =====
Jessica Santiago feels Jessica is happy to help out.  ({'neg': 0.0, 'neu': 0.385, 'pos': 0.615, 'compound': 0.7506})
Rebecca Simmons feels Rebecca is happy that Jessica will be helping out.  ({'neg': 0.0, 'neu': 0.543, 'pos': 0.457, 'compound': 0.7096})
==================

Success! You took 2.3333333333333335 steps to solve Jessica Santiago and Rebecca Simmons's problem!

Goodbye!
```



