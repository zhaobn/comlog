# %%
import math
import pandas as pd
from Rational_rules import *

# %%
# read data
exp_data = pd.read_json('../for_exp/config_2.json')
gen_ids = [100, 55, 94, 71, 31, 19, 41, 3]
gen_ids.sort()
gen_data = []
for id in gen_ids:
  data = exp_data[exp_data.trial_id==id]
  _, agent, recipient, result = list(data.iloc[0])
  converted = (f'Egg(S{agent[1]},O{agent[4]})', recipient[-2], result[-2])
  gen_data.append(converted)

# set up prediction df
N_TERMS = 17
predictions = pd.DataFrame({'terms': [str(x) for x in list(range(N_TERMS))]})

# initialize model
productions = [
  ['S', ['add(A,A)', 'sub(A,A)', 'mult(A,A)']],
  ['A', ['S', 'B']],
  ['B', ['C', 'D']],
  ['C', ['stripe(d)', 'spot(d)', 'stick(d)']],
  ['D', ['0', '1', '2', '3']]
]
rt_model = Rational_rules(productions, cap=40)

# %%
# read rules
rules = pd.read_csv('data/ld_comb2.csv', index_col=0)

for (ix, gd) in enumerate(gen_data):
  probs = [0.]*N_TERMS
  for rix in rules.index:
    rule, lp = list(rules.iloc[rix])
    term, term_lp = rt_model.predict((rule, lp), gd)
    probs[int(term)] += math.exp(term_lp)
  normed_probs = [x/sum(probs) for x in probs]
  df_gen = pd.DataFrame({f'prob_{ix+1}': normed_probs})
  predictions = pd.concat([predictions, df_gen], axis=1)

# Save carefully
predictions.to_csv('data/exp_4/combine_preds_b.csv')

# %%
