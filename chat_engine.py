
import os
import sys
import subprocess
import traceback
import shutil

if not 'TRANSFORMERS_CACHE' in os.environ:
    os.environ['TRANSFORMERS_CACHE'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ai_models'
    )

print(f'Using TRANSFORMERS_CACHE = {os.environ["TRANSFORMERS_CACHE"]}')
os.makedirs(os.environ['TRANSFORMERS_CACHE'], exist_ok=True)

# See https://github.com/Pan-ML/panml
try:
    import panml
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', '--user', 'panml'
    ])
    import panml

from panml.models import ModelPack

# See https://github.com/Pan-ML/panml/wiki/8.-Supported-models
#model_to_use = 'gpt2'
#model_to_use = 'cerebras/Cerebras-GPT-590M'
#model_to_use = 'cerebras/Cerebras-GPT-13B'
#model_to_use = 'google/flan-t5-base' # 250m parameter model
#model_to_use = 'google/flan-t5-xxl' # 11b parameter model, needs 64+gb ram
model_to_use = 'google/flan-t5-xl' # 3b parameter model, uses maybe 12gb ram.
#model_to_use = 'google/flan-t5-large' # 780m parameter model
#model_to_use = 'EleutherAI/gpt-j-6b'
model_source = 'huggingface'

print()
print(f'Loading {model_to_use} from {model_source}')
print()

lm = ModelPack(model=model_to_use, source=model_source)

print()
print('Talk to the bot!')
print()

# Try to nudge the language model in a useful direction by
# beginning the conversation w/ a prompt.
conversation = [
    'You are a successful manager who creatively solves employee problems. Please solve Person1\'s problem by talking to them.'
]

while True:
    user_input = input('User> ')
    if user_input == 'q' or user_input == 'quit' or user_input == 'exit':
        print(f'Got {user_input}, exiting...')
        break

    user_input = user_input.strip()

    if len(user_input) < 1:
        continue
    
    conversation.append(f'Person1: {user_input}')

    # See https://github.com/Pan-ML/panml/blob/main/panml/core/llm/huggingface.py#L88
    prompt_text = '\n'.join(conversation)
    output = lm.predict(prompt_text, max_length=3500)

    bot_text = output['text'].strip()
    bot_text = bot_text.lstrip('Person1: ')
    bot_text = bot_text.lstrip('person1: ')
    bot_text = bot_text.lstrip('Person2: ')
    bot_text = bot_text.lstrip('person2: ')
    if len(bot_text) < 2:
        bot_text = output['text'].strip()

    print(f'BOT> {bot_text}')

    conversation.append(f'Person2: {bot_text}')



print('Goodbye!')

