
# %%
import sys
sys.path.append('../')
from program_sim import *
from task import *

# Setting up
SAVE_DIR = 'samples/construct'
TOP_N = 3
EXCEPTS = 0
LEARN_ITER = 150
GEN_ITER = 1000

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
    transformed['agent'] = transform_obj(data['agent'].values[0], 1)
    transformed['recipient'] = transform_obj(data['recipient'].values[0], 1)
    transformed['result'] = transform_obj(data['result'].values[0], 1)
    task_data[item].append(transformed)

all_frames = pd.read_csv('../data/task_frames.csv',index_col=0)
padding = len(str(LEARN_ITER))
data_len_a = len(task_data['learn_a'])
data_len_b = len(task_data['learn_b'])


# %%
# Learning phase A
pl = Task_lib(pd.read_csv('../data/task_pm.csv', index_col=0, na_filter=False))
g1 = Task_gibbs(pl, task_data['learn_a'], iteration=LEARN_ITER)
g1.run(all_frames, top_n=TOP_N, exceptions_allowed=EXCEPTS, save_prefix=f'{SAVE_DIR}_a')


# Gen predictions A
a_learned = pd.read_csv(f'{SAVE_DIR}_a_lib_{str(LEARN_ITER).zfill(padding)}_{str(data_len_a).zfill(padding)}.csv', index_col=0, na_filter=False)
a_gen = sim_for_all(task_data['gen'],  Task_lib(a_learned), 1000)
a_gen.to_csv('construct_preds_a.csv')


# Learning phase B
g2 = Task_gibbs(Task_lib(a_learned), task_data['learn_b'], iteration=LEARN_ITER)
g2.run(all_frames, top_n=TOP_N, exceptions_allowed=EXCEPTS, save_prefix=f'{SAVE_DIR}_b')


# Gen predictions B
b_learned = pd.read_csv(f'{SAVE_DIR}_b_lib_{str(LEARN_ITER).zfill(padding)}_{str(data_len_b).zfill(padding)}.csv', index_col=0, na_filter=False)
b_gen = sim_for_all(task_data['gen'], Task_lib(b_learned), 1000)
b_gen.to_csv('construct_preds_b.csv')
