
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




