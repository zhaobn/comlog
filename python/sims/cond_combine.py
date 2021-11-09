
# %%
import sys
sys.path.append('../')
from program_sim import *
from task_terms import *

# Setting up
SAVE_DIR = 'samples/'
TOP_N = 3
EXCEPTS = 0
LEARN_ITER = 150
GEN_ITER = 1000

# Prep data
all_data = pd.read_json('../for_exp/config.json')
task_ids = {
  'learn_a': [23, 42, 61],
  'learn_b': [35, 50, 65],
  'learn_c': [27, 31, 35],
  'gen': [100, 71, 78, 55, 47, 83, 9, 3],
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
# Gen predictions A
a_learned = pd.read_csv(f'{SAVE_DIR}combine_0a_post_samples.csv', index_col=0, na_filter=False)
a_gen = sim_for_all(task_data['gen'],  Program_lib(a_learned), 1000)
a_gen.to_csv('combine_preds_a.csv')

# Gen predictions B
b_learned = pd.read_csv(f'{SAVE_DIR}combine_0b_post_samples.csv', index_col=0, na_filter=False)
b_gen = sim_for_all(task_data['gen'], Program_lib(b_learned), 1000)
b_gen.to_csv('combine_preds_b.csv')
