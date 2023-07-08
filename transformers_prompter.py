
# Example runs, passing in models + task strings:
#
#   python transformers_prompter.py gpt2 text-generation
#   python transformers_prompter.py deepset/roberta-base-squad2 question-answering
#   python transformers_prompter.py hadiqaemi/t5-github-readme-summarizer summarization
#
# Ensure your model supports the task!
#

import os, sys
import traceback


os.environ['TRANSFORMERS_CACHE'] = os.environ.get('TRANSFORMERS_CACHE', os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'transformers_cache'
))
os.makedirs(os.environ['TRANSFORMERS_CACHE'], exist_ok=True)
print('Saving models in', os.environ['TRANSFORMERS_CACHE'])

import code, subprocess, traceback
runner_env = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'runner_env'
)
os.makedirs(runner_env, exist_ok=True)
print('Putting python libs in ', runner_env)
sys.path.append(runner_env)


try:
    import torch
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={runner_env}', 'torch', 'torchvision', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cu118'
    ])
    import torch


try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={runner_env}', 'transformers[torch]'
    ])
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

try:
    import xformers
except:
    traceback.print_exc()
    subprocess.run([
        sys.executable, '-m', 'pip', 'install', f'--target={runner_env}', 'xformers'
    ])
    import xformers


# model_name = 'bigscience/bloom'
# model_name = 'gpt2'
model_name = 'lmsys/longchat-13b-16k' if len(sys.argv) < 2 else sys.argv[1]

print(f'Loading model {model_name}')

# See https://huggingface.co/docs/transformers/main/en/main_classes/pipelines#transformers.pipeline.task
# for tasks
task = 'text-generation' if len(sys.argv) < 3 else sys.argv[2]
print(f'Using model to perform task {task}')

cuda_dev_num = 0
print(f'Using CUDA device: {torch.cuda.get_device_name(cuda_dev_num)}')
print(f'num_workers = {os.cpu_count()}')

generator = pipeline(
        task=task,
        model=model_name,
        num_workers=os.cpu_count(),
        device=cuda_dev_num
)

try:

    # Used for Q+A/summary context, From https://www.vertiv.com/en-emea/about/news-and-insights/articles/educational-articles/three-phase-power-what-it-is-and-the-benefits-it-brings/
    three_phase_power_article_text = '''
Three-phase alternating current (AC) power is commonly used to deliver electricity to data centers as well as commercial and industrial buildings that house power-hungry machinery. There’s good reason for that, because 3-phase power can deliver more power with greater efficiency, as opposed to single-phase AC power. Single-phase AC is the type commonly used for most household and light commercial applications, such as lighting and small appliances. On this page, we’ll explain why that’s the case and the key differences between single- and 3-phase power systems.

Why we need 3-phase power

The ability to deliver ever-increasing amounts of power is especially important as data centers and server rooms continue to see higher densities. More powerful computing systems are being packed into the same spaces that once housed servers that drew only a fraction of the electrical power that today’s computers and networks demand.

It wasn’t long ago that a single IT rack of 10 servers would draw a total of five kilowatts (kW) of power. Today, that same rack may hold dozens of servers that collectively draw 20 or 30 kW. At those kinds of levels, you naturally want to put a premium on efficiency, as even a small percentage improvement in power consumption will mean significant dollar savings over time.

Wiring is another issue. Consider a 15 kW rack. Using single-phase at 120 volts AC (VAC) power, it takes 125 amps to power the rack, which would require a wire that’s almost one-quarter inch in diameter (AWG 4) — too thick to work with easily, not to mention expensive. Because 3-phase is more efficient, it can deliver the same power (and more) using smaller wiring. To support the same 15 kW rack using 3-phase power requires three wires capable of supplying 42 amps (AWG 10), which are a fraction of the size — each less than one-tenth of an inch in diameter.
 
Single-phase AC power explained

So, what is 3-phase power, exactly? And where should we use it?

Before diving into that discussion, it’s helpful to start with an understanding of single-phase AC power.

Single-phase AC power uses a three-wire delivery system consisting of one “hot” wire, a neutral wire, and a ground. With AC power, the power current or voltage reverses periodically, flowing one way on the hot wire that delivers power to the load and the other way on the neutral wire. A full power cycle takes place during a 360-degree phase change, and the voltage reverses itself 50 or 60 times per second, depending on the system in use in different parts of the world. In North America, it’s 60 times or 60 hertz (Hz).

Importantly, the two current-carrying legs are always 180 degrees apart. To visualize this, think of the power as riding a wave, technically a sine wave with a defined frequency and amplitude. In each cycle, the waves on each wire pass through zero amplitude twice at the same time (see Figure 1). During these instances, no power is delivered to the load.

3-Phase Power Figure 1a

3-Phase Power Figure 1b

Figure 1

These ever-so-brief interruptions make no difference for residential and commercial building applications such as office environments but have significant implications for the motors that power large machinery, as well as computers and other IT equipment.

Diving into 3-phase power

As its name implies, 3-phase power systems provide three separate currents, each separated by one-third of the time it takes to complete a full cycle. But, as opposed to single-phase, where the two hot legs are always 180 degrees apart, with 3-phase, the currents are separated by 120 degrees.

In Figure 2 below, you’ll see that when any one line is at its peak current, the other two are not. For example, when phase 1 is at its positive peak, phases 2 and 3 are both at -0.5. This means, unlike single-phase current, there’s no point at which no power is being delivered to the load. In fact, at six different positions in each phase, one of the lines is at peak positive or negative position.

For practical purposes, this means the collective amount of power supplied by all three currents remains constant; you don’t have cyclical peaks and valleys as with single-phase.

Computers and many motors used in heavy machinery are designed with this in mind. They can draw a steady stream of constant power, rather than having to account for the variation inherent in single-phase AC power. As a result, they use less energy.

As an analogy, think of a single-cylinder versus a three-cylinder engine. Both operate on a four-stroke model (intake, compression, power, exhaust). With a single-cylinder engine, you get only one “power” cycle for every four strokes of the cylinder, which provides for rather uneven power delivery. A three-stroke engine, by contrast, will provide power in three alternating phases (again separated by 120 degrees), for smoother, more constant and efficient power.

3-Phase Power Figure 2

 Figure 2

Benefits of 3-phase power

Among the benefits that 3-phase power brings is the ability to deliver nearly twice the power of single-phase systems without requiring twice the number of wires. It’s not three times as much power, as one might expect, because in practice, you typically take one hot line and connect it to another hot line.

To understand how 3-phase delivers more power, one must do the math. The formula for single-phase power is Power = Voltage (V) x Current (I) x Power Factor (PF). If we assume the load on the circuit is resistive only, power factor is unity (or one) which reduces the formula to P = V x I. If we consider a 120-volt circuit supporting 20 amps, the power is equal to 2,400 watts.

The formula for power of a 3-phase circuit is Power = Voltage (V) x Current (I) x Power Factor (PF) x square root of three. If we assume the load on the circuit is resistive only, power factor is unity (or one) which reduces the formula to P = V x I x square root of three. If we consider a 120-volt, 3-phase circuit and each phase supports 20 amps, the formula works out to 120 Volts x 20 Amps x 1.732 = 4,157 watts. This is how 3-phase can deliver nearly twice the power of single-phase systems. This is a simplified example, but it can be used to investigate the additional power available from circuits supporting higher voltages (e.g. 208 or 480 volts) or currents (e.g. 30 amps or greater).

This kind of capacity comes in handy when it comes to powering racks of IT gear. Whereas once it was the norm to use single-phase power to a rack, as densities in IT racks increase, it becomes less feasible and practical. All the cabling, conductors, and sockets become larger, more expensive, and increasingly difficult to work with.

Delivering 3-phase power directly to the server rack enables you to use less expensive cabling and other components, all while delivering more power. It does, however, require paying attention to the load on each circuit, to ensure they’re balanced and do not exceed circuit capacity.

To learn more about how 3-phase power works and the benefits it brings, visit: https://www.vertiv.com/en-us/products-catalog/critical-power/uninterruptible-power-supplies-ups.
'''

    print(f'generator = {generator}')
    if task == 'text-generation':
        print(f'>>> {generator("Hello user, my name is", max_new_tokens=200)}')
    elif task == 'question-answering':
        print(f'>>> What delivers more power? >>> {generator(context=three_phase_power_article_text, question="What delivers more power?", max_new_tokens=200)}')
    elif task == 'summarization':
        print(f'>>> {generator(three_phase_power_article_text, min_length=10, max_length=50)}')
except:
    traceback.print_exc()

print('''
# 
# Run text generation/model prompting (see task types) like:
#   text-generation:    generator('Hello, my name is', max_new_tokens=200)
#   question-answering: generator(context="The sky has been a few different colors lately, ranging from red to blue. Yesterday the sky was red. Today the sky is bluer.", question="What color is the sky?", max_new_tokens=200)
#   summarization:      generator(long_article_text, min_length=10, max_length=50)
# 
# Args for generator's __call__ are documented at https://huggingface.co/docs/transformers/main/en/main_classes/pipelines#transformers.TextGenerationPipeline.__call__
#
#
'''.strip())

vars = globals()
vars.update(locals())
code.interact(local=vars)

