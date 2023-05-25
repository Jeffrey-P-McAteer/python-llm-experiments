
import os
import sys
import subprocess
import traceback
import shutil

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
model_to_use = 'google/flan-t5-base'
model_source = 'huggingface'

print()
print(f'Loading {model_to_use} from {model_source}')
print()

lm = ModelPack(model=model_to_use, source=model_source)

#output = lm.predict('hello world is')
#print(output['text'])

#prompts = [
#    {'prepend': 'you are a company manager'},
#    {'prepend': 'help the employee solve their problems'},
#    {'prepend': 'summarise to the original question'},
#]

print()
print('Talk to the bot!')
print()

# Even numbers are user, odd numbers will be bot output.
conversation = []

while True:
    user_input = input('User> ')
    if user_input == 'q' or user_input == 'quit' or user_input == 'exit':
        print(f'Got {user_input}, exiting...')
        break

    user_input = user_input.strip()
    
    conversation.append(f'User: {user_input}')

    # See https://github.com/Pan-ML/panml/blob/main/panml/core/llm/huggingface.py#L88
    prompt_text = '\n'.join(conversation)
    output = lm.predict(prompt_text, max_length=250)

    bot_text = output['text'].strip()
    bot_text = bot_text.lstrip('User: ')
    bot_text = bot_text.lstrip('user: ')
    bot_text = bot_text.lstrip('Bot: ')
    bot_text = bot_text.lstrip('bot: ')

    print(f'BOT> {bot_text}')

    conversation.append(f'Bot: {bot_text}')



print('Goodbye!')

