# %% Imports
import pandas as pd
from Rational_rules import *

# %% Model specification
productions = [
  ['S', ['add(A,A)', 'sub(A,A)', 'mult(A,A)']],
  ['A', ['S', 'B']],
  ['B', ['C', 'D']],
  ['C', ['stripe(d)', 'spot(d)', 'stick(d)']],
  ['D', ['0', '1', '2', '3']]
]
rat_rules_model = Rational_rules(productions, cap=100)

# %% Prep data
exp_1_data = pd.read_json('../for_exp/config.json')
exp_1_ids = {
  'learn_a': [23, 42, 61],
  'learn_b': [35, 50, 65],
  'learn_c': [27, 31, 35],
  'gen': [100, 71, 78, 55, 47, 83, 9, 3],
}
exp_1_ids_list = exp_1_ids['learn_a'] + exp_1_ids['learn_b'] + exp_1_ids['learn_c']

exp_2_data = pd.read_json('../for_exp/config_2.json')
exp_2_ids = {
  'learn_a': [7, 10, 13],
  'learn_b': [67, 50, 33],
  'learn_c': [27, 47, 67],
  'gen': [100, 55, 94, 71, 31, 19, 41, 3]
}
exp_2_ids_list = exp_2_ids['learn_a'] + exp_2_ids['learn_b'] + exp_2_ids['learn_c']

ld_all = {}
for (ix, id) in enumerate(exp_1_ids_list+exp_2_ids_list):
  if ix < len(exp_1_ids_list):
    data = exp_1_data[exp_1_data.trial_id==id]
    dt_name = f'exp1_ld{ix+1}'
  else:
    data = exp_2_data[exp_2_data.trial_id==id]
    dt_name = f'exp2_ld{ix-len(exp_1_ids_list)+1}'

  _, agent, recipient, result = list(data.iloc[0])
  converted = (f'Egg(S{agent[1]},O{agent[4]})', recipient[-2], result[-2])
  ld_all[dt_name] = converted


# %% Learning phase
N = 10000
sampled_rules = pd.DataFrame({
  'rule': pd.Series(dtype='str'), 'log_prob': pd.Series(dtype='float'),
})
s1 = sampled_rules.copy()
s2 = sampled_rules.copy()
s3 = sampled_rules.copy()
s12 = sampled_rules.copy()
s13 = sampled_rules.copy()

d1 = sampled_rules.copy()
d2 = sampled_rules.copy()
d3 = sampled_rules.copy()
d12= sampled_rules.copy()
d13 = sampled_rules.copy()

def save_dfs():
  s1.drop_duplicates(ignore_index=True).to_csv('data/s1.csv')
  s2.drop_duplicates(ignore_index=True).to_csv('data/s2.csv')
  s3.drop_duplicates(ignore_index=True).to_csv('data/s3.csv')
  s12.drop_duplicates(ignore_index=True).to_csv('data/s12.csv')
  s13.drop_duplicates(ignore_index=True).to_csv('data/s13.csv')
  d1.drop_duplicates(ignore_index=True).to_csv('data/d1.csv')
  d2.drop_duplicates(ignore_index=True).to_csv('data/d2.csv')
  d3.drop_duplicates(ignore_index=True).to_csv('data/d3.csv')
  d12.drop_duplicates(ignore_index=True).to_csv('data/d12.csv')
  d13.drop_duplicates(ignore_index=True).to_csv('data/d13.csv')


# %%
k = 0
while k<N:
  generated = rat_rules_model.generate_tree()
  if generated is not None:
    # evaluate on data
    learned = {}
    for dt in ld_all.items():
      dt_name, data = dt
      learned[dt_name] = Rational_rules.evaluate(generated, data)[0] # Just the bool
    # add to df
    to_append = pd.DataFrame({'rule': [generated[0]], 'log_prob':[generated[1]]})
    if (learned['exp1_ld1'] and learned['exp1_ld2'] and learned['exp1_ld3']):
      s1 = pd.concat([s1, to_append], ignore_index=True)
    if (learned['exp1_ld4'] and learned['exp1_ld5'] and learned['exp1_ld6']):
      s2 = pd.concat([s2, to_append], ignore_index=True)
    if (learned['exp1_ld7'] and learned['exp1_ld8'] and learned['exp1_ld9']):
      s3 = pd.concat([s3, to_append], ignore_index=True)
    if (
      learned['exp1_ld1'] and learned['exp1_ld2'] and learned['exp1_ld3'] and
      learned['exp1_ld4'] and learned['exp1_ld5'] and learned['exp1_ld6']
    ):
      s12 = pd.concat([s12, to_append], ignore_index=True)
    if (
      learned['exp1_ld1'] and learned['exp1_ld2'] and learned['exp1_ld3'] and
      learned['exp1_ld7'] and learned['exp1_ld8'] and learned['exp1_ld9']
    ):
      s13 = pd.concat([s13, to_append], ignore_index=True)

    if (learned['exp2_ld1'] and learned['exp2_ld2'] and learned['exp2_ld3']):
      d1 = pd.concat([d1, to_append], ignore_index=True)
    if (learned['exp2_ld4'] and learned['exp2_ld5'] and learned['exp2_ld6']):
      d2 = pd.concat([d2, to_append], ignore_index=True)
    if (learned['exp2_ld7'] and learned['exp2_ld8'] and learned['exp2_ld9']):
      d3 = pd.concat([d3, to_append], ignore_index=True)
    if (
      learned['exp2_ld1'] and learned['exp2_ld2'] and learned['exp2_ld3'] and
      learned['exp2_ld4'] and learned['exp2_ld5'] and learned['exp2_ld6']
    ):
      d12 = pd.concat([d12, to_append], ignore_index=True)
    if (
      learned['exp2_ld1'] and learned['exp2_ld2'] and learned['exp2_ld3'] and
      learned['exp2_ld7'] and learned['exp2_ld8'] and learned['exp2_ld9']
    ):
      d13 = pd.concat([d13, to_append], ignore_index=True)

    # save df
    if k>10000 and k%500==0:
      save_dfs()
  k+=1

save_dfs()

# %%
