
# %% Packages
import sys
sys.path.append('../')

from multiprocessing import Pool

from program_sim import *
from task_terms import *
from program_inf import *

# %% Setting up
COND = 'flip'
DVAR = 'stripes'
TOP_N = 3
EXCEPTS = 0
LEARN_ITERS = [10,50,100] + list(range(200, 1001, 200)) + list(range(2000, 10001, 2000)) + list(range(20000, 100001, 20000))
# LEARN_ITERS = [10,50,100]

# %% Prep data
task_data = {
  'learn_a': [],
  'learn_b': [],
  'gen': [],
}
tasks = pd.read_csv('../../data/tasks/exp_3.csv', index_col=0)
tasks = tasks[tasks['condition']==COND]

learn_a_tasks = tasks[tasks['batch']=='A'].reset_index()
for i in learn_a_tasks.index:
  task_dt = learn_a_tasks.iloc[i]
  task_obj = {
    'agent': eval(f"Egg(S{task_dt['stripe']},O{task_dt['dot']})"),
    'recipient': task_dt['block'],
    'result':  task_dt['result_block']
  }
  task_data['learn_a'].append(task_obj)

learn_b_tasks = tasks[tasks['batch']=='B'].reset_index()
for i in learn_b_tasks.index:
  task_dt = learn_b_tasks.iloc[i]
  task_obj = {
    'agent': eval(f"Egg(S{task_dt['stripe']},O{task_dt['dot']})"),
    'recipient': task_dt['block'],
    'result':  task_dt['result_block']
  }
  task_data['learn_b'].append(task_obj)

gen_tasks = tasks[tasks['batch']=='gen'].reset_index()
for i in gen_tasks.index:
  task_dt = gen_tasks.iloc[i]
  task_obj = {
    'agent': eval(f"Egg(S{task_dt['stripe']},O{task_dt['dot']})"),
    'recipient': task_dt['block'],
    'result':  task_dt['result_block']
  }
  task_data['gen'].append(task_obj)

all_frames = pd.read_csv('../data/task_frames.csv',index_col=0)

# %%
def getResults (iter):
  # Learning phase A
  pl = Program_lib(pd.read_csv('../data/task_pm.csv', index_col=0, na_filter=False))
  g1 = Gibbs_sampler(pl, all_frames, task_data['learn_a'], iteration=iter)
  g1.run(top_n=TOP_N, save_prefix=f'data/process_{iter}/{COND}_a_', save_intermediate=False)

  # Gen predictions A
  a_learned = pd.read_csv(f'data/process_{iter}/{COND}_a_post_samples.csv', index_col=0, na_filter=False)
  a_gen = sim_for_all(task_data['gen'],  Program_lib(a_learned), 1000)
  a_gen.to_csv(f'data/process_{iter}/{COND}_preds_a.csv')

  # Learning phase B
  pl2 = Program_lib(pd.read_csv(f'data/process_{iter}/{COND}_a_post_samples.csv', index_col=0, na_filter=False))
  pl2.update_lp_adaptor()
  pl2.update_overall_lp()
  g2 = Gibbs_sampler(pl2, all_frames, task_data['learn_b'], iteration=iter, lib_is_post=True)
  g2.run(top_n=TOP_N, save_prefix=f'data/process_{iter}/{COND}_b_', save_intermediate=False)

  # Gen predictions B
  b_learned = pd.read_csv(f'data/process_{iter}/{COND}_b_post_samples.csv', index_col=0, na_filter=False)
  b_gen = sim_for_all(task_data['gen'],  Program_lib(b_learned), 10000)
  b_gen.to_csv(f'data/process_{iter}/{COND}_preds_b.csv')

# %%
if __name__ == '__main__':
  with Pool(6) as p:
    p.map(getResults, [iter for iter in LEARN_ITERS])

# %%
