
import os
import sys
import subprocess
import traceback
import shutil
import time
import random

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
        sys.executable, '-m', 'pip', 'install', '--user', 'faker'
    ])
    from faker import Faker

# Used for pronouns of names
try:
     import gender_guesser.detector as gender
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', '--user', 'gender-guesser'
    ])
    import gender_guesser.detector as gender


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



game_seed = 0
if len(sys.argv) > 1:
    game_seed = int(sys.argv[1])
else:
    game_seed = int(time.time())

print(f'game_seed = {game_seed}')
print('Remember the game seed if you want to play the same game again by passing it as Arg1!')
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
        
        self.age = random.randint(18, 72)

        self.employee_description = employee_description.format(
            name=self.name,
            first_name=self.first_name,
            last_name=self.last_name,
            job=self.job,
            gender=self.gender,
            age=self.age,
        )
    
    def tell(self, text):
        pass

    def is_happy(self):

        return False

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
model_to_use = 'google/flan-t5-xl' # 3b parameter model, uses maybe 12gb ram.
#model_to_use = 'google/flan-t5-large' # 780m parameter model
#model_to_use = 'EleutherAI/gpt-j-6b'
model_source = 'huggingface'

print()
print(f'Loading {model_to_use} from {model_source}')
print()

lm = ModelPack(model=model_to_use, source=model_source)


# Try to nudge the language model in a useful direction by
# beginning the conversation w/ a prompt.
conversation = [
    employee_a.get_description(),
    employee_b.get_description(),
    game_problem
]

while True:
    user_input = input('Manager> ')
    if user_input == 'q' or user_input == 'quit' or user_input == 'exit':
        print(f'Got {user_input}, exiting...')
        break

    user_input = user_input.strip()

    if len(user_input) < 1:
        continue
    
    conversation.append(f'Manager: {user_input}')

    prompt_text = '\n'.join(conversation)
    prompt_text += f'{employee_a.first_name}: ' # Prompt for employee A next statement
    employee_a_output = lm.predict(prompt_text, max_length=3500)

    employee_a_text = employee_a_output['text']
    employee_a_text = ':'.join(employee_a_text.split(':')[1:]) # Trim first ABC: beginning of the line
    if len(employee_a_text) < 2:
        employee_a_text = employee_a_output['text'].strip()


    print(f'{employee_a.first_name}: {employee_a_text}')
    conversation.append(f'{employee_a.first_name}: {employee_a_text}')


    prompt_text = '\n'.join(conversation)
    prompt_text += f'{employee_b.first_name}: ' # Prompt for employee B next statement
    employee_b_output = lm.predict(prompt_text, max_length=3500)

    employee_b_text = employee_b_output['text']
    employee_b_text = ':'.join(employee_b_text.split(':')[1:]) # Trim first ABC: beginning of the line
    if len(employee_b_text) < 2:
        employee_b_text = employee_b_output['text'].strip()


    print(f'{employee_b.first_name}: {employee_b_text}')
    conversation.append(f'{employee_b.first_name}: {employee_b_text}')





print('Goodbye!')

