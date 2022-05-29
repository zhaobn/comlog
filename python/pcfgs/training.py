# %% Imports
import random

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
random.seed(10)

# %% Prep data
exp_data = pd.read_json('../for_exp/config_2.json')
exp_ids = {
  'learn_a': [7, 10, 13],
  'learn_b': [67, 50, 33],
  'learn_c': [27, 47, 67],
}
exp_ids_list = exp_ids['learn_a'] + exp_ids['learn_b'] + exp_ids['learn_c']

ld_all = {}
for (ix, id) in enumerate(exp_ids_list):
  data = exp_data[exp_data.trial_id==id]
  dt_name = f'ld{ix+1}'

  _, agent, recipient, result = list(data.iloc[0])
  converted = (f'Egg(S{agent[1]},O{agent[4]})', recipient[-2], result[-2])
  ld_all[dt_name] = converted


# %% Learning phase
N = 10000
sampled_rules = pd.DataFrame({
  'rule': pd.Series(dtype='str'), 'log_prob': pd.Series(dtype='float'),
})
d1 = sampled_rules.copy()
d2 = sampled_rules.copy()
d3 = sampled_rules.copy()
d12 = sampled_rules.copy()
d13 = sampled_rules.copy()

def save_dfs():
  d1.drop_duplicates(ignore_index=True).to_csv('data/d1.csv')
  d2.drop_duplicates(ignore_index=True).to_csv('data/d2.csv')
  d3.drop_duplicates(ignore_index=True).to_csv('data/d3.csv')
  d12.drop_duplicates(ignore_index=True).to_csv('data/d12.csv')
  d13.drop_duplicates(ignore_index=True).to_csv('data/d13.csv')

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
    if (learned['ld1'] and learned['ld2'] and learned['ld3']):
      d1 = pd.concat([d1, to_append], ignore_index=True)
    if (learned['ld4'] and learned['ld5'] and learned['ld6']):
      d2 = pd.concat([d2, to_append], ignore_index=True)
    if (learned['ld7'] and learned['ld8'] and learned['ld9']):
      d3 = pd.concat([d3, to_append], ignore_index=True)
    if (
      learned['ld1'] and learned['ld2'] and learned['ld3'] and
      learned['ld4'] and learned['ld5'] and learned['ld6']
    ):
      d12 = pd.concat([d12, to_append], ignore_index=True)
    if (
      learned['ld1'] and learned['ld2'] and learned['ld3'] and
      learned['ld7'] and learned['ld8'] and learned['ld9']
    ):
      d13 = pd.concat([d13, to_append], ignore_index=True)
  k+=1

save_dfs()

# %%
