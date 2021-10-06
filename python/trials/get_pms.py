
# %%
import sys
sys.path.append('../')
from program_inf import *

# %% Setting up
SAVE_DIR = 'tmp/'
TOP_N = 3
EXCEPTS = 3
LEARN_ITER = 5

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

all_learn_data = task_data['learn_a'] + task_data['learn_b']

# Run Gibbs
all_frames = pd.read_csv('../data/task_frames.csv',index_col=0)
pl = Program_lib(pd.read_csv('../data/task_pm.csv', index_col=0, na_filter=False))
g1 = Gibbs_sampler(pl, all_frames, all_learn_data, iteration=LEARN_ITER)
g1.run(top_n=TOP_N, exceptions_allowed=EXCEPTS, save_prefix=SAVE_DIR, save_intermediate=True)

# %%
