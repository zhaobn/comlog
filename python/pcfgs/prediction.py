# %%
import math
import pandas as pd
from Rational_rules import *

# %%
# initialize model
N_TERMS = 17
productions = [
  ['S', ['add(A,A)', 'sub(A,A)', 'mult(A,A)']],
  ['A', ['S', 'B']],
  ['B', ['C', 'D']],
  ['C', ['stripe(d)', 'spot(d)', 'stick(d)']],
  ['D', ['0', '1', '2', '3']]
]
rt_model = Rational_rules(productions, cap=100)

# %%
# get preds per condition
configs = [
  ('d1', 'construct_preds_a'),
  ('d12', 'construct_preds_b'),

  ('d2', 'decon_preds_a'),
  ('d12', 'decon_preds_b'),

  ('d1', 'combine_preds_a'),
  ('d13', 'combine_preds_b'),

  ('d3', 'flip_preds_a'),
  ('d13', 'flip_preds_b'),
]

for df, cond in configs:
  # read data
  gen_data = []
  tasks = pd.read_csv('../../data/tasks/exp_2.csv', index_col=0)
  tasks = tasks[tasks['condition']=='construct']
  gen_tasks = tasks[tasks['batch']=='gen'].reset_index()
  for i in gen_tasks.index:
    task_dt = gen_tasks.iloc[i]
    task_obj = (f"Egg(S{task_dt['stripe']},O{task_dt['dot']})", str(task_dt['block']), str( task_dt['result_block']))
    gen_data.append(task_obj)

  # read learned rules
  rules = pd.read_csv(f'data/{df}.csv', index_col=0)

  # Initialize prediction df
  predictions = pd.DataFrame({'terms': [str(x) for x in list(range(N_TERMS))]})

  # Get predictions
  for (ix, gd) in enumerate(gen_data):
    probs = [0.]*N_TERMS
    for rix in rules.index:
      rule, lp = list(rules.iloc[rix])
      term, term_lp = rt_model.predict((rule, lp), gd)
      probs[int(term)] += math.exp(term_lp)
    normed_probs = [x/sum(probs) for x in probs]
    df_gen = pd.DataFrame({f'prob_{ix+1}': normed_probs})
    predictions = pd.concat([predictions, df_gen], axis=1)

  # Save
  predictions.to_csv(f'data/{cond}.csv')



# %%
