
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


DEBUG = False
if 'DEBUG' in os.environ:
    DEBUG = bool(os.environ['DEBUG'])

print(f'DEBUG = {DEBUG}')

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

llm_server_folder = os.path.join(os.path.dirname(__file__), 'llm-server-folder')
if not os.path.exists(llm_server_folder):
    os.makedirs(llm_server_folder, exist_ok=True)

# Ensure a server process is running by creating a file that the server always deletes.
server_live_check_txt = os.path.join(llm_server_folder, 'server-live-check.txt')
with open(server_live_check_txt, 'w') as fd:
    fd.write('Test!')

# We expect the server to delete the file within 5 seconds, if it still exists we must launch llm_server.py
for _ in range(0, 6*4):
    time.sleep(1.0/4.0)
    if not os.path.exists(server_live_check_txt):
        break

if os.path.exists(server_live_check_txt):
    # Spawn a server!
    # See https://github.com/Pan-ML/panml/wiki/8.-Supported-models
    model_to_use = 'google/flan-t5-xl' # 3b parameter model, uses maybe 12gb ram.
    model_source = 'huggingface'
    server_cmd_args = [
        sys.executable, os.path.join(os.path.dirname(__file__), 'llm_server.py'),
            model_source, model_to_use, llm_server_folder,
    ]
    print()
    print('> ', ' '.join(server_cmd_args))
    print()

    subprocess.Popen(server_cmd_args)

    # Also wait until it removes server-live-check.txt
    print(f'Waiting for server to come up...')
    while os.path.exists(server_live_check_txt):
        time.sleep(2)
        print(f'Waiting for server to come up...')
    print(f'Server is up!')


def predict(text):
    predict_txt = os.path.join(llm_server_folder, 'predict.txt')
    with open(predict_txt, 'w') as fd:
        fd.write(text)

    response_txt = os.path.join(llm_server_folder, 'response.txt')
    while not os.path.exists(response_txt):
        time.sleep(0.1)

    response_s = ''
    with open(response_txt, 'r') as fd:
        response_s = fd.read()
        if not isinstance(response_s, str):
            response_s = response_s.decode('utf-8')

    os.remove(response_txt)
    if os.path.exists(predict_txt):
        os.remove(predict_txt)

    return response_s

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

os.environ['MAX_GAME_TOKENS'] = str(MAX_GAME_TOKENS)
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
    def get_happiness_score(self, conversation, sia):
        prompt_text = '\n'.join(conversation)
        prompt_text += '\n'
        prompt_text += f'How does {self.first_name} feel?'

        text = predict(prompt_text)
        
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
        employee_a_scores, employee_a_feeling  = employee_a.get_happiness_score(conversation, sia)
        employee_b_scores, employee_b_feeling = employee_b.get_happiness_score(conversation, sia)
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

        next_speaker_out = predict(prompt_text)
        
        next_to_speak = next_speaker_out["text"]

        if DEBUG:
            print(f'DEBUG: next_to_speak={next_to_speak}')
        
        if employee_a.first_name.lower() in next_to_speak.lower():
            # Prompt Employee A for next spoken dialog
            prompt_text = '\n'.join(conversation)
            prompt_text += '\n'
            prompt_text += f'{employee_a.first_name}: '
            employee_a_text = predict(prompt_text)
            employee_a_text = ':'.join(employee_a_text.split(':')[1:]) # Trim first ABC: beginning of the line
        
        if employee_b.first_name.lower() in next_to_speak.lower():
            # Prompt Employee A for next spoken dialog
            prompt_text = '\n'.join(conversation)
            prompt_text += '\n'
            prompt_text += f'{employee_b.first_name}: '
            employee_b_text = predict(prompt_text)
            employee_b_text = ':'.join(employee_b_text.split(':')[1:]) # Trim first ABC: beginning of the line
            

        # Now output stuff
        if employee_a.first_name.lower() in next_to_speak.lower():
            print(f'{employee_a.first_name}: {employee_a_text}')
            conversation.append(f'{employee_a.first_name}: {employee_a_text}')
        
        if employee_b.first_name.lower() in next_to_speak.lower():
            print(f'{employee_b.first_name}: {employee_b_text}')
            conversation.append(f'{employee_b.first_name}: {employee_b_text}')
    


print('Goodbye!')

