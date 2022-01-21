# %%
import sys
sys.path.append('../')
from program_lib import *
from program_sim import transform_obj

# %%
# Basic setup
pm_task = pd.read_csv('../data/task_pm.csv', index_col=0, na_filter=False)[['terms', 'arg_types', 'return_type', 'type', 'is_init', 'count']]
pl = Program_lib(pm_task)
pl.initial_comp_lp()
pl.update_lp_adaptor()
pl.update_overall_lp()

# Load frames
frames_d1 = pd.read_csv('../data/task_frames.csv',index_col=0)


# Get data
all_data = pd.read_json('../for_exp/config.json')
task_ids = {
  'all': [ 23, 42, 61, 35, 50, 65, 27, 31, 35 ],
}

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


# %%
# Find consistent programs with fixed depth
filtered = pd.DataFrame(columns=['terms','log_prob','construct_a','construct_b','decon_a','decon_b','combine_a','combine_b'])
for k in frames_d1.index:
  # unfold frame
  unfolded = pl.unfold_program(frames_d1.at[k,'terms'], task_data['all'])
  # check each program
  for i in unfolded.index:
    # check consistency with each data point
    for j in range(len(task_data['all'])):
      unfolded.at[i,f'data_{j+1}'] = pl.check_program(unfolded.at[i,'terms'], task_data['all'][j])
    # check for test batches
    pass_construct_a = unfolded.at[i, 'data_1'] & unfolded.at[i, 'data_2'] & unfolded.at[i, 'data_3']
    pass_decon_a = unfolded.at[i, 'data_4'] & unfolded.at[i, 'data_5'] & unfolded.at[i, 'data_6']
    pass_cons_all = pass_construct_a & pass_decon_a
    pass_combine_all = pass_construct_a & unfolded.at[i, 'data_7'] & unfolded.at[i, 'data_8'] & unfolded.at[i, 'data_9']
    unfolded.at[i, 'construct_a'] = pass_construct_a
    unfolded.at[i, 'construct_b'] = pass_cons_all
    unfolded.at[i, 'decon_a'] = pass_decon_a
    unfolded.at[i, 'decon_b'] = pass_cons_all
    unfolded.at[i, 'combine_a'] = pass_construct_a
    unfolded.at[i, 'combine_b'] = pass_combine_all
    if pass_construct_a or pass_decon_a or pass_cons_all or pass_combine_all:
      pass_checks = unfolded.loc[i,['terms','log_prob','construct_a','construct_b','decon_a','decon_b','combine_a','combine_b']]
      filtered = filtered.append(pass_checks, ignore_index=True)
      filtered.to_csv('enum_fd1.csv')

# %%
# Enumerate programs with d=1 for predictions
all_programs = pd.DataFrame(columns=['terms','log_prob'])
for k in frames_d1.index:
  # unfold frame
  unfolded = pl.unfold_program(frames_d1.at[k,'terms'], task_data['all'])
  all_programs = all_programs.append(unfolded.loc[:,['terms','log_prob']], ignore_index=True)
  all_programs.to_csv('all_programs_d1.csv')

# %%
