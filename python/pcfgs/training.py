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
  'gen': [82, 8, 20, 4, 98, 48, 71, 40],
}
exp_1_ids_list = exp_1_ids['learn_a'] + exp_1_ids['learn_b'] + exp_1_ids['learn_c']

exp_2_data = pd.read_json('../for_exp/config_2.json')
exp_2_ids = {
  'learn_a': [7, 10, 13],
  'learn_b': [67, 50, 33],
  'learn_c': [27, 47, 67],
  'gen': [100, 55, 94, 71, 31, 19, 41, 3],
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
N = 100
sampled_rules = pd.DataFrame({
  'rule': pd.Series(dtype='str'), 'log_prob': pd.Series(dtype='float'),
})

ld_colnames = pd.DataFrame(columns=list(ld_lookup.keys()))
ld_colnames.astype('int32')

sampled_rules = pd.concat([sampled_rules, ld_colnames], axis=1)

# %%
while len(sampled_rules)<N:
  generated = rat_rules_model.generate_tree()
  if generated is not None:
    # evaluate on data
    learned = {}
    for dt in ld_all.items():
      dt_name, data = dt
      learned[dt_name] = [Rational_rules.evaluate(generated, data)[0]] # Just the bool
    # add to df
    if sum(x[0] for x in list(learned.values()))>0:
      to_append = pd.DataFrame({'rule': [generated[0]], 'log_prob':[generated[1]]})
      to_append = pd.concat([to_append, pd.DataFrame.from_dict(learned)], axis=1)
      sampled_rules = pd.concat([sampled_rules, to_append], ignore_index=True)
    # save df
    if len(sampled_rules)%100==0:
      sampled_rules.to_csv('data/test.csv')

sampled_rules.to_csv('data/test.csv')

# %%
