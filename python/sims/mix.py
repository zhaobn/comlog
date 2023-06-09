# %% Packages
import sys
sys.path.append('../')

from multiprocessing import Pool

from program_sim import *
from task_terms import *
from program_inf import *

# # %%
# def getMixLib(run_id, pro_id, condition, phase):
#   # get libs
#   if condition == 'decon':
#     d1 = None
#   else:
#     d1 = pd.read_csv(f'run_{run_id}/data_allframes/process_{pro_id}/{condition}_{phase}_post_samples.csv', index_col=0)
#     d1 = d1[d1['is_init']<1]

#   d2 = pd.read_csv(f'run_{run_id}/data_d2/process_{pro_id}/{condition}_{phase}_post_samples.csv', index_col=0)
#   d2 = d2[d2['is_init']<1]


#   # mix them
#   lib = pd.read_csv('../data/task_pm.csv', index_col=0, na_filter=False)

#   for i in range(pro_id):
#     # sample caches
#     sampled = None
#     if condition == 'decon':
#       if np.random.random() < math.exp(-1)/(math.exp(-1)/math.exp(-2)):
#         sampled = d2.sample(n=3, replace=True, weights=d2['count'])

#     else:
#       if np.random.random() > math.exp(-1)/(math.exp(-1)/math.exp(-2)):
#         sampled = d2.sample(n=3, replace=True, weights=d2['count'])
#       else:
#         sampled = d1.sample(n=3, replace=True, weights=d1['count'])

#     if sampled is not None:
#       sampled['count'] = 1
#       sampled = sampled.groupby(['terms','arg_types','return_type','type','comp_lp']).size().reset_index(name='count')

#       # Add to lib
#       merged_df = pd.merge(lib, sampled, how='outer', on=['terms','arg_types','return_type','type']).fillna(0)
#       merged_df['count'] = merged_df['count_x'] + merged_df['count_y']

#       # Increase counter
#       set_df = (merged_df
#         .query('count_x>0')[['terms','arg_types','return_type','type','is_init','count','comp_lp_x']]
#         .rename(columns={'comp_lp_x': 'comp_lp'}))
#         # Take care of newly-created programs
#       to_set_df = (merged_df
#         .query('count_x==0')[['terms','arg_types','return_type','type','count','comp_lp_y']]
#         .rename(columns={'comp_lp_y': 'comp_lp'}))
#       to_set_df['is_init'] = 0
#       # Merge & take care of probabilities
#       lib = pd.concat([set_df, to_set_df], ignore_index=True)

#     # save
#     lib.to_csv(f'run_{run_id}/data_geo/process_{pro_id}/{condition}_{phase}_post_samples.csv', index=False)


# # %%
# def run_mix(run):
#   if run == 0:
#     iters = [16, 32, 64, 128, 256, 512, 1024]
#   else:
#     iters = list(range(1,11)) + [ 2**x for x in range(4,11) ]

#   for iter in iters:
#     for c in ['decon', 'construct', 'combine', 'flip']:
#       for p in ['a',  'b']:
#         getMixLib(run, iter, c, p)

# # %%
# if __name__ == '__main__':
#   with Pool(4) as p:
#     p.map(run_mix, [run for run in range(4)])




# %%
# Predictions
task_data = {
  'gen': [],
}
tasks = pd.read_csv('../../data/tasks/exp_1.csv', index_col=0)
gen_tasks = tasks[tasks['condition']=='combine']
gen_tasks = gen_tasks[gen_tasks['batch']=='gen'].reset_index()

for i in gen_tasks.index:
  task_dt = gen_tasks.iloc[i]
  task_obj = {
    'agent': eval(f"Egg(S{task_dt['stripe']},O{task_dt['dot']})"),
    'recipient': task_dt['block'],
    'result':  task_dt['result_block']
  }
  task_data['gen'].append(task_obj)


def get_preds(run_id, pro_id, condition, phase):
  print(f'run {run_id} | process {pro_id} ')
  lib = pd.read_csv(f'run_{run_id}/data_geo/process_{pro_id}/{condition}_{phase}_post_samples.csv', na_filter=False)
  gen = sim_for_all(task_data['gen'],  Program_lib(lib), 10000)
  gen.to_csv(f'run_{run_id}/data_geo/process_{pro_id}/{condition}_preds_{phase}.csv')

def run_preds(run_id):
  for iter in list(range(1,11)) + [ 2**x for x in range(4,11) ]:
    for c in ['decon', 'construct', 'combine', 'flip']:
      for p in ['a',  'b']:
        get_preds(run_id, iter, c, p)

# %%
if __name__ == '__main__':
  with Pool(10) as p:
    p.map(run_preds, [run for run in range(42)])
