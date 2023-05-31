
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


if not 'TRANSFORMERS_CACHE' in os.environ:
    os.environ['TRANSFORMERS_CACHE'] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'ai_models'
    )

print(f'Using TRANSFORMERS_CACHE = {os.environ["TRANSFORMERS_CACHE"]}')
os.makedirs(os.environ['TRANSFORMERS_CACHE'], exist_ok=True)

# Used for names
try:
     from faker import Faker
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'faker'
    ])
    from faker import Faker

# Used for pronouns of names
try:
     import gender_guesser.detector as gender
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'gender-guesser'
    ])
    import gender_guesser.detector as gender

# Used to ask employees how they feel about the situation for background game scoring.
try:
    from nltk.sentiment import SentimentIntensityAnalyzer
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'nltk'
    ])
    from nltk.sentiment import SentimentIntensityAnalyzer

import nltk
nltk.download('vader_lexicon', download_dir=os.environ["TRANSFORMERS_CACHE"])
nltk.data.path.append(os.environ["TRANSFORMERS_CACHE"])


# See https://github.com/Pan-ML/panml
try:
    import panml
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={py_packages_folder}', 'panml'
    ])
    import panml

from panml.models import ModelPack


game_seed = 0
if len(sys.argv) > 1:
    game_seed = int(sys.argv[1])
else:
    game_seed = int(time.time())

print(f'game_seed = {game_seed}')
print('Remember the game seed if you want to play the same game again by passing it as Arg1!')
MAX_GAME_TOKENS = int(os.environ.get('MAX_GAME_TOKENS', '12500'))
print(f'MAX_GAME_TOKENS = {MAX_GAME_TOKENS}')
print()

random.seed(game_seed)

class Employee():
    def __init__(self, fake, employee_description):
        self.name = fake.name()
        self.first_name = self.name.split()[0]
        self.last_name = self.name.split()[-1]

        self.job = fake.job()

        self.gender = gender.Detector().get_gender(self.name.split()[0])
        if self.gender == 'andy':
            self.gender = random.choice(['male', 'female'])
        self.gender = self.gender.replace('mostly_', '')
        self.gender = self.gender.replace('half_', '')
        
        self.age = random.randint(18, 72)

        self.employee_description = employee_description.format(
            name=self.name,
            first_name=self.first_name,
            last_name=self.last_name,
            job=self.job,
            gender=self.gender,
            age=self.age,
        )
    
    # Number from -1 to 1, -1 means mad 1 means happy.
    def get_happiness_score(self, lm, conversation, sia):
        prompt_text = '\n'.join(conversation)
        prompt_text += '\n'
        prompt_text += f'How does {self.first_name} feel?'

        output = lm.predict(prompt_text, max_length=MAX_GAME_TOKENS)
        text = output['text']

        scores = sia.polarity_scores(text)
        # eg {'neg': 0.0, 'neu': 0.328, 'pos': 0.672, 'compound': 0.6249}

        # print(f'   DEBUG> How does {self.first_name} feel? {text} . {scores}')
        
        # Compound is closer to 1.0 when 'pos' is close to 1.0 
        return scores, text
        

    def get_description(self):
        return self.employee_description

fake = Faker()
fake.seed_instance(game_seed)

employee_a = Employee(fake, '{name} is a {age}-year-old {gender}. {first_name} is the {job} around here.')
employee_b = Employee(fake, '{name} is a {age}-year-old {gender}. {first_name} is our {job} around here.')


problems = [
    '{a.first_name} decided to throw a party after work and did not invite {b.first_name}. {b.first_name} feels left out.',
    '{a.first_name} is putting day-old pizza boxes in the trash and not taking the trash out. {b.first_name} ends up always doing the work!',
    '{a.first_name} has ruined {b.first_name}\'s project!',
]

game_problem = random.choice(problems).format(
    a=employee_a,
    b=employee_b
)


print()
print('You are a manager and two employees with a problem have come into your office.')
print('Talk them through their problem until both employees are happy.')
print()


print(employee_a.get_description())
print()
print(employee_b.get_description())
print()
print(game_problem)
print()


# See https://github.com/Pan-ML/panml/wiki/8.-Supported-models
#model_to_use = 'gpt2'
#model_to_use = 'cerebras/Cerebras-GPT-590M'
#model_to_use = 'cerebras/Cerebras-GPT-13B'
#model_to_use = 'google/flan-t5-base' # 250m parameter model
#model_to_use = 'google/flan-t5-xxl' # 11b parameter model, needs 64+gb ram
#model_to_use = 'google/flan-t5-xl' # 3b parameter model, uses maybe 12gb ram.
#model_to_use = 'google/flan-t5-large' # 780m parameter model
#model_to_use = 'EleutherAI/gpt-j-6b'


model_to_use = 'google/flan-t5-xl' # 3b parameter model, uses maybe 12gb ram.
#model_to_use = 'cerebras/Cerebras-GPT-590M'
#model_to_use = 'EleutherAI/gpt-neo-2.7B'
#model_to_use = 'google/flan-t5-large'
#model_to_use = 'gpt2'

model_source = 'huggingface'

print()
print(f'Loading {model_to_use} from {model_source}')
print()

lm = ModelPack(model=model_to_use, source=model_source, model_args={'gpu': True})

# Try to nudge the language model in a useful direction by
# beginning the conversation w/ a prompt.
conversation = [
    employee_a.get_description(),
    employee_b.get_description(),
    game_problem
]

sia = SentimentIntensityAnalyzer()

skip_happiness_check = False

while True:
    if not skip_happiness_check:
        print('===== Scores =====')
        employee_a_scores, employee_a_feeling  = employee_a.get_happiness_score(lm, conversation, sia)
        employee_b_scores, employee_b_feeling = employee_b.get_happiness_score(lm, conversation, sia)
        print(f'{employee_a.name} feels {employee_a_feeling} ({employee_a_scores})')
        print(f'{employee_b.name} feels {employee_b_feeling} ({employee_b_scores})')
        print('==================')

        at_least_one_is_unhappy = employee_a_scores.get('neg', 0.0) > 0.1 or employee_b_scores.get('neg', 0.0) > 0.1
        at_least_one_is_mildly_happy = employee_a_scores.get('pos', 0.0) > 0.3 or employee_b_scores.get('pos', 0.0) > 0.3
        
        if not at_least_one_is_unhappy and at_least_one_is_mildly_happy:
            print()
            print(f'Success! You took {len(conversation) / 3} steps to solve {employee_a.name} and {employee_b.name}\'s problem!')
            print()
            break
    
    skip_happiness_check = False
    user_input = input('Manager> ')
    user_input = user_input.strip()

    if user_input == 'q' or user_input == 'quit' or user_input == 'exit':
        print(f'Got {user_input}, exiting...')
        break

    if len(user_input) < 1:
        skip_happiness_check = True # Same game state
        continue
    
    conversation.append(f'Manager: {user_input}')

    # Now ask the AI model who speaks next, and continue prompting for employee_a.first_name / employee_b.first_name
    # until "Manager" is selected as the next speaker.
    next_to_speak = ''
    while not 'manager' in next_to_speak.lower():
        prompt_text = '\n'.join(conversation)
        prompt_text += '\n'
        prompt_text += 'Who speaks next?'

        next_speaker_out = lm.predict(prompt_text, max_length=MAX_GAME_TOKENS)
        
        next_to_speak = next_speaker_out["text"]

        print(f'DEBUG: next_to_speak={next_to_speak}')
        
        if employee_a.first_name.lower() in next_to_speak.lower():
            # Prompt Employee A for next spoken dialog
            prompt_text = '\n'.join(conversation)
            prompt_text += '\n'
            prompt_text += f'{employee_a.first_name}: '
            employee_a_output = lm.predict(prompt_text, max_length=MAX_GAME_TOKENS)
            employee_a_text = employee_a_output['text']
            employee_a_text = ':'.join(employee_a_text.split(':')[1:]) # Trim first ABC: beginning of the line
            if len(employee_a_text) < 2:
                employee_a_text = employee_a_output['text'].strip()
            #print(f'{employee_a.first_name}: {employee_a_text}')
            #conversation.append(f'{employee_a.first_name}: {employee_a_text}')
        
        if employee_b.first_name.lower() in next_to_speak.lower():
            # Prompt Employee A for next spoken dialog
            prompt_text = '\n'.join(conversation)
            prompt_text += '\n'
            prompt_text += f'{employee_b.first_name}: '
            employee_b_output = lm.predict(prompt_text, max_length=MAX_GAME_TOKENS)
            employee_b_text = employee_b_output['text']
            employee_b_text = ':'.join(employee_b_text.split(':')[1:]) # Trim first ABC: beginning of the line
            if len(employee_b_text) < 2:
                employee_b_text = employee_b_output['text'].strip()
            #print(f'{employee_b.first_name}: {employee_b_text}')
            #conversation.append(f'{employee_b.first_name}: {employee_b_text}')
        
        # Now output stuff
        if employee_a.first_name.lower() in next_to_speak.lower():
            print(f'{employee_a.first_name}: {employee_a_text}')
            conversation.append(f'{employee_a.first_name}: {employee_a_text}')
        
        if employee_b.first_name.lower() in next_to_speak.lower():
            print(f'{employee_b.first_name}: {employee_b_text}')
            conversation.append(f'{employee_b.first_name}: {employee_b_text}')
    


print('Goodbye!')

