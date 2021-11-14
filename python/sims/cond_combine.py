
# %%
import sys
sys.path.append('../')
from program_sim import *
from task_terms import *
from program_inf import *

# Setting up
COND = 'combine'
TOP_N = 3
EXCEPTS = 0
LEARN_ITER = 200

# Prep data
all_data = pd.read_json('../for_exp/config_2.json')
task_ids = {
  'learn_a': [7, 10, 13],
  'learn_b': [27, 47, 67],
  'gen': [100, 55, 94, 71, 31, 19, 41, 3]
}
task_ids['gen'].sort()

task_data = {}
for item in task_ids:
  task_data[item] = []
  for ti in task_ids[item]:
    transformed = {}
    data = all_data[all_data.trial_id==ti]
    transformed['agent'] = eval(transform_obj(data['agent'].values[0], 1))
    transformed['recipient'] = transform_obj(data['recipient'].values[0], 0)
    transformed['result'] = transform_obj(data['result'].values[0], 0)
    task_data[item].append(transformed)

all_frames = pd.read_csv('../data/task_frames.csv',index_col=0)

# %%
# Learning phase A
pl = Program_lib(pd.read_csv('../data/task_pm.csv', index_col=0, na_filter=False))
g1 = Gibbs_sampler(pl, all_frames, task_data['learn_a'], iteration=LEARN_ITER)
g1.run(top_n=TOP_N, save_prefix=f'samples/{COND}a_', save_intermediate=False)

# Gen predictions A
a_learned = pd.read_csv(f'samples/{COND}a_post_samples.csv', index_col=0, na_filter=False)
a_gen = sim_for_all(task_data['gen'],  Program_lib(a_learned), 1000)
a_gen.to_csv('preds/{COND}_preds_a.csv')

# Learning phase B
pl2 = Program_lib(pd.read_csv(f'samples/{COND}a_post_samples.csv', index_col=0, na_filter=False))
pl2.update_lp_adaptor()
pl2.update_overall_lp()
g2 = Gibbs_sampler(pl2, all_frames, task_data['learn_b'], iteration=LEARN_ITER, lib_is_post=True)
g2.run(top_n=TOP_N, save_prefix=f'samples/{COND}b_', save_intermediate=False)

# Gen predictions B
b_learned = pd.read_csv(f'samples/{COND}b_post_samples.csv', index_col=0, na_filter=False)
b_gen = sim_for_all(task_data['gen'],  Program_lib(b_learned), 1000)
b_gen.to_csv('preds/{COND}_preds_b.csv')


# %%
