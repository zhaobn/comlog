
#%%
import pandas as pd
from task_configs import *
from task import *

# %%
programs_df = pd.read_csv('data/t4_filtered_01_06.csv', index_col=0).reset_index(drop=True)

# %%
all_pairs_df = pd.read_csv('data/gen_pairs.csv', index_col=0)
eq_class_df = pd.DataFrame(columns=['pred_list', 'terms', 'count'])

for i in range(len(programs_df)):
  terms = programs_df.at[i, 'terms']
  pm = Program(eval(terms))
  pred_list = []
  for j in range(len(all_pairs_df)):
    data = [eval(all_pairs_df.at[j,'agent']), eval(all_pairs_df.at[j,'recipient'])]
    pred = pm.run(data)
    pred_rounded = 0 if pred < 0 else pred
    pred_list.append(pred_rounded)
  pred_list_joined = ','.join([str(x) for x in pred_list])
  matched_idx = eq_class_df.index[eq_class_df['pred_list'] == pred_list_joined].tolist()
  if len(matched_idx) == 0: # new eq class
    eq_class_df = eq_class_df.append(pd.DataFrame({
      'pred_list': [pred_list_joined],
      'terms': [terms],
      'count': [1]
    }), ignore_index=True)
  else:
    found_idx = matched_idx[0]
    found_terms = eq_class_df.at[found_idx, 'terms']
    if len(terms) < len(found_terms):
      eq_class_df.at[found_idx, 'terms'] = terms
    eq_class_df.at[found_idx, 'count'] += 1

# %%
