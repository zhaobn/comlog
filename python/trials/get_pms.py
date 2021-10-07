
# %%
import sys
sys.path.append('../')
from program_inf import *

# %% Setting up

cond = 'construct'
save_dir_1 = f'tmp/{cond}_a_'
save_dir_2 = f'tmp/{cond}_b_'

EXCEPTS = 0
TOP_N = 3
LEARN_ITER = 100


# Prep data
all_data = pd.read_json('../for_exp/config.json')
task_ids = {
  'learn_a': [23, 42, 61],
  'learn_b': [35, 50, 65],
  'gen': [82, 8, 20, 4, 98, 48, 71, 40],
}
task_ids['gen'].sort()

task_data = {}
for item in task_ids:
  task_data[item] = []
  for ti in task_ids[item]:
    transformed = {}
    data = all_data[all_data.trial_id==ti]
    _, agent, recipient, result = list(data.iloc[0])
    transformed['agent'] = eval(f'Egg(S{agent[1]},O{agent[4]})')
    transformed['recipient'] = int(recipient[-2])
    transformed['result'] = int(result[-2])
    task_data[item].append(transformed)

task_configs = {
  'construct': {
    'phase_1': task_data['learn_a'],
    'phase_2': task_data['learn_a'] + task_data['learn_b']
  },
  'combine': {
    'phase_1': task_data['learn_a'],
    'phase_2': task_data['learn_b']
  },
  'decon': {
    'phase_1': task_data['learn_b'],
    'phase_2': task_data['learn_b'] + task_data['learn_a']
  }
}
# Run Gibbs
all_frames = pd.read_csv('../data/task_frames.csv',index_col=0)
pl = Program_lib(pd.read_csv('../data/task_pm.csv', index_col=0, na_filter=False))
g1 = Gibbs_sampler(pl, all_frames, task_configs[cond]['phase_1'], iteration=LEARN_ITER)
g1.run(top_n=TOP_N, exceptions_allowed=EXCEPTS, save_prefix=save_dir_1, save_intermediate=True)

post_pms = g1.post_samples.query('arg_types=="egg_num"&return_type=="num"&type=="program"')
post_to_add = post_pms.sample(TOP_N, weights='count')
post_lib = Program_lib(pd.concat([g1.init_lib, post_to_add], ignore_index=True))
post_lib.update_lp_adaptor()
post_lib.update_overall_lp()

g2 = Gibbs_sampler(post_lib, all_frames, task_configs[cond]['phase_2'], iteration=LEARN_ITER)
g2.run(top_n=TOP_N, exceptions_allowed=EXCEPTS, save_prefix=save_dir_2, save_intermediate=True)

# %%
