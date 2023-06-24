
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

llm_server_folder = os.environ.get('LLM_SERVER_FOLDER', os.path.join(os.path.dirname(__file__), 'llm-server-folder') )
if not os.path.exists(llm_server_folder):
    os.makedirs(llm_server_folder, exist_ok=True)

# Ensure a server process is running by creating a file that the server always deletes.
if not 'NOAUTOSPAWN' in os.environ:
    print('NOAUTOSPAWN not in environ, checking if server is running...')
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
        # python3.10 llm_server.py huggingface google/flan-t5-xxl ./llm-server-folder/
        print()
        print('> ', ' '.join(server_cmd_args))
        print()

        if DEBUG:
            subprocess.Popen(server_cmd_args)
        else:
            # Ensure server is silent
            subprocess.Popen(server_cmd_args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Also wait until it removes server-live-check.txt
        print(f'Waiting for server to come up...')
        while os.path.exists(server_live_check_txt):
            time.sleep(1)
            print(f'Waiting for server to come up...')
        print(f'Server is up!')
else:
    print('NOAUTOSPAWN in environ, continuing w/o checking if server process is running!')
    

def predict(text):
    predict_txt = os.path.join(llm_server_folder, 'predict.txt')
    with open(predict_txt, 'w') as fd:
        fd.write(text)

    response_txt = os.path.join(llm_server_folder, 'response.txt')
    while not os.path.exists(response_txt):
        time.sleep(0.1)
    time.sleep(0.1)

    response_s = ''
    for _ in range(0, 100): # Poll file for up to 10s for a non-empty response string
        with open(response_txt, 'r') as fd:
            response_s = fd.read()
            if not isinstance(response_s, str):
                response_s = response_s.decode('utf-8')
        if len(response_s) > 0:
            break
        else:
            time.sleep(0.1)

    while os.path.exists(response_txt):
        time.sleep(0.1)
        try:
            os.remove(response_txt)
            break
        except:
            pass

    while os.path.exists(predict_txt):
        time.sleep(0.1)
        try:
            os.remove(predict_txt)
            break
        except:
            pass

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

        if 'male' in self.gender:
            self.subject_pronoun = 'he'
            self.object_pronoun = 'him'
        else:
            self.subject_pronoun = 'she'
            self.object_pronoun = 'her'
        
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

class PublicComment:
    def __init__(self, comment):
        self.comment = comment

class PrivateComment:
    def __init__(self, comment):
        self.comment = comment

class GameScene:
    def __init__(self, public_problem_format_s, private_problem_format_s, employee_a, employee_b):
        self.public_problem_format_s = public_problem_format_s
        self.private_problem_format_s = private_problem_format_s
        self.employee_a = employee_a
        self.employee_b = employee_b
        # Holds objects of type PublicComment or PrivateComment.
        # PrivateComment is not known to the player (manager).
        self.conversation = [
            PublicComment(public_problem_format_s.format(a=self.employee_a, b=self.employee_b)),
            PrivateComment(private_problem_format_s.format(a=self.employee_a, b=self.employee_b)),
        ]
    
    def get_entire_conversation(self):
        entire_convo_text = []
        for entry in self.conversation:
            entire_convo_text.append(entry.comment)
        return entire_convo_text

    def get_public_conversation(self):
        pub_convo_text = []
        for entry in self.conversation:
            if isinstance(entry, PublicComment):
                pub_convo_text.append(entry.comment)
        return pub_convo_text

    def add_to_conversation(self, comment):
        if not isinstance(comment, str):
            comment = str(comment)
        # If the comment is >75% either a or b's first_name, do not add it.
        comment_wo_usernames = (comment.lower()
                                      .replace(self.employee_a.first_name.lower(), '')
                                      .replace(self.employee_b.first_name.lower(), '') )
        
        # if the words w/o usernames are <= 25% of comment then the comment was >75% names
        if len(comment_wo_usernames) < len(comment) * 0.25:
            return

        self.conversation.append(PublicComment( comment.strip() ))



fake = Faker()
fake.seed_instance(game_seed)

employee_a = Employee(fake, '{name} is a {age}-year-old {gender}. {first_name} is a {job} around here.')
employee_b = Employee(fake, '{name} is a {age}-year-old {gender}. {first_name} is a {job} around here.')


# Fun new approach - some of the conversation/background is hidden from the player!
problems = [
    GameScene(
        '{a.first_name} decided to throw a party after work and did not invite {b.first_name}. {b.first_name} feels left out.',
        ' '.join([
            '{b.first_name} feels sad because people in the office have been unfairly making fun of {b.object_pronoun}.'
            '{a.first_name} does not want to admit it but they secretly hate {b.first_name} because of the rumours around the office.'
        ]),
        employee_a, employee_b,
    ),
    GameScene(
        '{a.first_name} decided to throw a party after work and did not invite {b.first_name}. {b.first_name} feels left out.',
        ' '.join([
            '{b.first_name} is very busy and can never find the free time to participate in social events, but does not want anyone to know they are so busy.',
            '{a.first_name} has been trying to invite {b.first_name} to their parties, but {b.first_name} seems to never get back to them.'
        ]),
        employee_a, employee_b,
    ),
    GameScene(
        '{a.first_name} has ruined {b.first_name}\'s project!',
        ' '.join([
            '{b.first_name} was working for months to build a useful tool and had asked {a.first_name} for help. {b.subject_pronoun} knows {a.first_name} is talented and can help with the project.',
            '{a.first_name} was trying to help but a part broke during construction. {a.first_name} is afraid they will be ridiculed if anyone finds out about the broken part!'
        ]),
        employee_a, employee_b,
    ),
]

game_problem = random.choice(problems)



print()
print('You are a manager and two employees with a problem have come into your office.')
print('Talk them through their problem until both employees are happy.')
print()


print(employee_a.get_description())
print()
print(employee_b.get_description())
print()
for line in game_problem.get_public_conversation():
    print(line)
print()

sia = SentimentIntensityAnalyzer()
skip_happiness_check = False
num_manager_steps = 0

while True:
    if not skip_happiness_check:
        print('===== Scores =====')
        employee_a_scores, employee_a_feeling  = employee_a.get_happiness_score(game_problem.get_entire_conversation(), sia)
        employee_b_scores, employee_b_feeling = employee_b.get_happiness_score(game_problem.get_entire_conversation(), sia)
        print(f'{employee_a.name} feels {employee_a_feeling} ({employee_a_scores})')
        print(f'{employee_b.name} feels {employee_b_feeling} ({employee_b_scores})')
        print('==================')

        at_least_one_is_unhappy = employee_a_scores.get('neg', 0.0) > 0.1 or employee_b_scores.get('neg', 0.0) > 0.1
        at_least_one_is_mildly_happy = employee_a_scores.get('pos', 0.0) > 0.3 or employee_b_scores.get('pos', 0.0) > 0.16
        
        if not at_least_one_is_unhappy and at_least_one_is_mildly_happy:
            print()
            print(f'Success! You took {num_manager_steps} steps to solve {employee_a.name} and {employee_b.name}\'s problem!')
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
    
    num_manager_steps += 1
    game_problem.add_to_conversation(f'Manager: {user_input}')

    # Now ask the AI model who speaks next, and continue prompting for employee_a.first_name / employee_b.first_name
    # until "Manager" is selected as the next speaker.
    next_to_speak = ''
    remaining_employee_messages = 7 # if we have more than 7 back-and-forths between employee agents, the manager interrupts.
    while not 'manager' in next_to_speak.lower():

        remaining_employee_messages -= 1

        prompt_text = '\n'.join(game_problem.get_entire_conversation())
        prompt_text += '\n'
        prompt_text += 'Who speaks next?'

        next_to_speak = predict(prompt_text)

        if DEBUG:
            print(f'DEBUG: next_to_speak={next_to_speak}')
        
        if employee_a.first_name.lower() in next_to_speak.lower():
            # Prompt Employee A for next spoken dialog
            prompt_text = '\n'.join(game_problem.get_entire_conversation())
            prompt_text += '\n'
            prompt_text += f'{employee_a.first_name}: '
            employee_a_text = predict(prompt_text)
            employee_a_text = ':'.join(employee_a_text.split(':')[1:]) # Trim first ABC: beginning of the line
        
        if employee_b.first_name.lower() in next_to_speak.lower():
            # Prompt Employee A for next spoken dialog
            prompt_text = '\n'.join(game_problem.get_entire_conversation())
            prompt_text += '\n'
            prompt_text += f'{employee_b.first_name}: '
            employee_b_text = predict(prompt_text)
            employee_b_text = ':'.join(employee_b_text.split(':')[1:]) # Trim first ABC: beginning of the line
            

        # Now output stuff
        if employee_a.first_name.lower() in next_to_speak.lower():
            print(f'{employee_a.first_name}: {employee_a_text}')
            game_problem.add_to_conversation(f'{employee_a.first_name}: {employee_a_text}')
        
        if employee_b.first_name.lower() in next_to_speak.lower():
            print(f'{employee_b.first_name}: {employee_b_text}')
            game_problem.add_to_conversation(f'{employee_b.first_name}: {employee_b_text}')

        # Repeat detection: if the last 3 conversation elements are the same, break!
        if len(game_problem.get_entire_conversation()) > 3 or remaining_employee_messages < 1:
            last_three = game_problem.get_entire_conversation()[-3:]
            if len(set(last_three)) <= 1 or remaining_employee_messages < 1:
                # They're all the same value!
                print('>>> Loop detected, breaking conversation!')
                break



print('Goodbye!')

