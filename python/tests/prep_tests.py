# %%
conditions = { 'r1': 1, 'r2': 2 }
components = { 'c1': 1, 'c2': 2, 'c3': 3, 'ca': 0 }
procs = { 'bat': False, 'inc': True}
use_samples = { 'top': False} # 'sam': True
top_n = [1, 2, 3]

# %%
imports = '''import pandas as pd
import sys
sys.path.append('..')
sys.path.append('../..')
from base_terms import *
from base_classes import Program
from program_lib import Program_lib
from program_inf import Gibbs_sampler
from program_sim import *
'''

def read_data(query_string):
  data_str = f"data = data.query('{query_string}')"
  text = ('''data = pd.read_csv('../data/designs.csv', index_col=0, na_filter=False)\n''' + data_str + '''
task_data = []
for i in range(len(data)):
  tdata = data.iloc[i].to_dict()
  tdata_fmt = {
    'agent': eval(tdata['agent']),
    'recipient': eval(tdata['recipient']),
    'result': eval(tdata['result'])
  }
  task_data.append(tdata_fmt)
pm_init = pd.read_csv('../data/pm_init_test.csv', index_col=0, na_filter=False)'''
)
  return text

def write(filename, content):
  f = open(f'{filename}.py', 'w')
  f.write(content)
  f.close()

# %%
for condition in conditions.items():
  for component in components.items():
    for proc in procs.items():
      for use_sample in use_samples.items():
        qs_data = f'condition=={condition[1]}'
        qs_data = qs_data + f'&component=={component[1]}' if component[0] != 'ca' else qs_data
        if use_sample[0] == 'sam':
          iter = 100
          filename = f'{condition[0]}_{component[0]}_{proc[0]}_{use_sample[0]}1'
          gibbs = f"\npt = Gibbs_sampler(Program_lib(pm_init, 0.1), task_data, inc={proc[1]}, iteration={iter})"
          run = f"\npt.run(save_prefix='{filename}/pm', sample=True, top_n=1)"
          content = imports + read_data(qs_data) + gibbs + run
          write(filename, content)
        else:
          for n in top_n:
            filename = f'{condition[0]}_{component[0]}_{proc[0]}_{use_sample[0]}{str(n)}'
            iter = 12 if component[0] == 'ca' else 4
            gibbs = f"\npt = Gibbs_sampler(Program_lib(pm_init, 0.1), task_data, inc={proc[1]}, iteration={iter})"
            run = f"\npt.run(save_prefix='{filename}/pm', sample=False, top_n={n})"
            content = imports + read_data(qs_data) + gibbs + run
            write(filename, content)

# %%
filenames = []
for condition in conditions.items():
  for component in components.items():
    for proc in procs.items():
      for use_sample in use_samples.items():
        if use_sample[0] == 'sam':
          filename = f'{condition[0]}_{component[0]}_{proc[0]}_{use_sample[0]}1'
          filenames.append(filename)
        else:
          for n in top_n:
            filename = f'{condition[0]}_{component[0]}_{proc[0]}_{use_sample[0]}{str(n)}'
            filenames.append(filename)

bash_cmds = ''
for f in filenames:
  bash_cmds += f"mkdir {f}\n"
  bash_cmds += f"screen -dmS {f} python {f}.py\n"

f = open('run_tests.sh', 'w')
f.write(bash_cmds)
f.close()

# %%
