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
rat_rules_model = Rational_rules(productions, cap=40)

# %% Prep data
ld_lookup = {}

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

  ld_lookup[dt_name] = id
  ld_all[dt_name] = converted


# %% Learning phase
N = 100000
sampled_rules = pd.DataFrame({
  'rule': pd.Series(dtype='str'), 'log_prob': pd.Series(dtype='float'),
})
df_A1 = sampled_rules.copy()
df_B1 = sampled_rules.copy()
df_C1 = sampled_rules.copy()
df_cons1 = sampled_rules.copy()
df_comb1 = sampled_rules.copy()

df_A2 = sampled_rules.copy()
df_B2 = sampled_rules.copy()
df_C2 = sampled_rules.copy()
df_cons2 = sampled_rules.copy()
df_comb2 = sampled_rules.copy()

def save_dfs():
  df_A1.drop_duplicates(ignore_index=True).to_csv('data/ld_A1.csv')
  df_B1.drop_duplicates(ignore_index=True).to_csv('data/ld_B1.csv')
  df_C1.drop_duplicates(ignore_index=True).to_csv('data/ld_C1.csv')
  df_cons1.drop_duplicates(ignore_index=True).to_csv('data/ld_cons1.csv')
  df_comb1.drop_duplicates(ignore_index=True).to_csv('data/ld_comb1.csv')
  df_A2.drop_duplicates(ignore_index=True).to_csv('data/ld_A2.csv')
  df_B2.drop_duplicates(ignore_index=True).to_csv('data/ld_B2.csv')
  df_C2.drop_duplicates(ignore_index=True).to_csv('data/ld_C2.csv')
  df_cons2.drop_duplicates(ignore_index=True).to_csv('data/ld_cons2.csv')
  df_comb2.drop_duplicates(ignore_index=True).to_csv('data/ld_comb2.csv')


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
    if learned['exp1_ld1'] and learned['exp1_ld2'] and learned['exp1_ld3']:
      df_A1 = pd.concat([df_A1, to_append], ignore_index=True)
    if learned['exp1_ld4'] and learned['exp1_ld5'] and learned['exp1_ld6']:
      df_B1 = pd.concat([df_B1, to_append], ignore_index=True)
    if learned['exp1_ld7'] and learned['exp1_ld8'] and learned['exp1_ld9']:
      df_C1 = pd.concat([df_C1, to_append], ignore_index=True)
    if (
      learned['exp1_ld1'] and learned['exp1_ld2'] and learned['exp1_ld3'] and
      learned['exp1_ld4'] and learned['exp1_ld5'] and learned['exp1_ld6']
    ):
      df_cons1 = pd.concat([df_cons1, to_append], ignore_index=True)
    if (
      learned['exp1_ld1'] and learned['exp1_ld2'] and learned['exp1_ld3'] and
      learned['exp1_ld7'] and learned['exp1_ld8'] and learned['exp1_ld9']
    ):
      df_comb1 = pd.concat([df_comb1, to_append], ignore_index=True)

    if learned['exp2_ld1'] and learned['exp2_ld2'] and learned['exp2_ld3']:
      df_A2 = pd.concat([df_A2, to_append], ignore_index=True)
    if learned['exp2_ld4'] and learned['exp2_ld5'] and learned['exp2_ld6']:
      df_B2 = pd.concat([df_B2, to_append], ignore_index=True)
    if learned['exp2_ld7'] and learned['exp2_ld8'] and learned['exp2_ld9']:
      df_C2 = pd.concat([df_C2, to_append], ignore_index=True)
    if (
      learned['exp2_ld1'] and learned['exp2_ld2'] and learned['exp2_ld3'] and
      learned['exp2_ld4'] and learned['exp2_ld5'] and learned['exp2_ld6']
    ):
      df_cons2 = pd.concat([df_cons2, to_append], ignore_index=True)
    if (
      learned['exp2_ld1'] and learned['exp2_ld2'] and learned['exp2_ld3'] and
      learned['exp2_ld7'] and learned['exp2_ld8'] and learned['exp2_ld9']
    ):
      df_comb2 = pd.concat([df_comb2, to_append], ignore_index=True)

    # save df
    if k>10000 and k%500==0:
      save_dfs()
  k+=1

save_dfs()

# %%
