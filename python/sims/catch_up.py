
# %% Packages
import sys
sys.path.append('../')

from multiprocessing import Pool

from program_sim import *
from task_terms import *

# %% Setting up
CONDS = [ 'construct', 'combine', 'flip' ]
DVAR = 'stripes'
TOP_N = 4
EXCEPTS = 0
iter = 512
# LEARN_ITERS = [ 2**(x+1) for x in range(10) ]
# LEARN_ITERS = list(range(100, 1501, 100)) + list(range(2000, 5001, 500))

# %% Prep data
task_data = {
  'gen': [],
}
tasks = pd.read_csv('../../data/tasks/exp_1.csv', index_col=0)
tasks = tasks[tasks['condition']=='construct']

gen_tasks = tasks[tasks['batch']=='gen'].reset_index()
for i in gen_tasks.index:
  task_dt = gen_tasks.iloc[i]
  task_obj = {
    'agent': eval(f"Egg(S{task_dt['stripe']},O{task_dt['dot']})"),
    'recipient': task_dt['block'],
    'result':  task_dt['result_block']
  }
  task_data['gen'].append(task_obj)

# %%
for COND in CONDS:
  b_learned = pd.read_csv(f'data/process_{iter}/{COND}_b_post_samples.csv', index_col=0, na_filter=False)
  b_gen = sim_for_all(task_data['gen'],  Program_lib(b_learned), 10000)
  b_gen.to_csv(f'data/process_{iter}/{COND}_preds_b.csv')
