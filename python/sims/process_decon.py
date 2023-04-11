
# %% Packages
import sys
sys.path.append('../')

from multiprocessing import Pool

from program_sim import *
from task_terms import *

# %% Setting up
COND = 'decon'
DVAR = 'stripes'
# TOP_N = 4
# EXCEPTS = 0
# LEARN_ITERS = [ 2**(x+1) for x in range(10) ]
# LEARN_ITERS = list(range(100, 1501, 100)) + list(range(2000, 5001, 500))

# %% Prep data
task_data = {
  'gen': [],
}
tasks = pd.read_csv('../../data/tasks/exp_1.csv', index_col=0)
tasks = tasks[tasks['condition']==COND]

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
pl = Program_lib(pd.read_csv('../data/task_pm.csv', index_col=0, na_filter=False))
gen_preds = sim_for_all(task_data['gen'],  pl, 10000)
gen_preds.to_csv(f'data/{COND}_preds.csv')
