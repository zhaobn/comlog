
# %%
import sys
sys.path.append('../')
from program_sim import *
from task import *


# Prep data
all_data = pd.read_json('../for_exp/config.json')
task_ids = {
  'learn_a': [35, 50, 65],
  'learn_b': [23, 42, 61],
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

# %%
# Learning phase A
pl = Task_lib(pd.read_csv('../data/task_pm.csv', index_col=0, na_filter=False))
g1 = Task_gibbs(pl, task_data['learn_a'], iteration=150)
g1.run(all_frames, top_n=3, exceptions_allowed=1, save_prefix='samples/discern_a')


# Gen predictions A
a_ppl = Task_lib(g1.all_programs)
a_gen = sim_for_all(task_data['gen'], a_ppl, 1000)
a_gen.to_csv('discern_preds_a.csv')


# Learning phase B
g2 = Task_gibbs(Task_lib(g1.all_programs), task_data['learn_b'], iteration=150)
g2.run(all_frames, top_n=3, exceptions_allowed=1, save_prefix='samples/discern_b')


# Gen predictions B
b_ppl = Task_lib(g2.all_programs)
b_gen = sim_for_all(task_data['gen'], b_ppl, 1000)
b_gen.to_csv('discern_preds_b.csv')
