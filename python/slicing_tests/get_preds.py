# %%
import sys
sys.path.append('../')
from program_lib import *
from program_sim import *
from helpers import normalize
import math

# %%
cond = 'construct'
phase = 'b'

filtered_programs = pd.read_csv('enum_fd1.csv')
all_programs = pd.read_csv('all_programs_d1.csv')

cond_programs = filtered_programs[filtered_programs[f'{cond}_{phase}']==True][['terms', 'log_prob']]
if len(cond_programs.index) < 1:
  cond_programs = all_programs.copy()

# %%
# Prep data
all_data = pd.read_json('../for_exp/config.json')
task_ids = {
  'learn_a': [23, 42, 61],
  'learn_b': [27, 31, 35],
  'gen': [100, 71, 78, 55, 47, 83, 9, 3]
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

# %%
# Get predictions
ret_df = pd.DataFrame({'terms': list(range(17))})
for i in range(len(task_data['gen'])):
  ret_df[f'count_{i+1}'] = 0
  ret_df[f'weight_{i+1}'] = 0.0

# For each program
for i in cond_programs.index:
  program = Program(eval(cond_programs.at[i,'terms']))
  # Loop through each generalization tasks
  for j in range(len(task_data['gen'])):
    # Get prediction
    data = task_data['gen'][j]
    pred = program.run([data['agent'], data['recipient']])
    # Safe caps
    pred = 0 if pred < 0 else pred
    pred = 16 if pred > 16 else pred
    # Record prediction
    ret_df.at[pred, f'count_{j+1}'] += 1
    ret_df.at[pred, f'weight_{j+1}'] += math.exp(cond_programs.at[i,'log_prob'])

# Normalize weights
for i in range(len(task_data['gen'])):
  ret_df[f'prob_{i+1}'] = normalize(ret_df[f'weight_{i+1}'])

# Return columns
cols_to_return = ['terms']
for i in range(len(task_data['gen'])):
  cols_to_return.append(f'count_{i+1}')
  cols_to_return.append(f'prob_{i+1}')

ret_df[cols_to_return].to_csv(f'preds/{cond}_preds_{phase}.csv')

# %%
