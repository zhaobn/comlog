
# %%
from os import rename
from numpy import column_stack
import pandas as pd

import sys
sys.path.append('../')
from task_configs import *
from task import *
from helpers import normalize, softmax

# %% Get all intermediate samples
programs_df = pd.read_csv('../test/si_inc/t5_filtered_001_002.csv', index_col=0).reset_index(drop=True)
programs_df = programs_df.append(pd.read_csv(f'../test/si_inv/t5_filtered_001_002.csv', index_col=0).reset_index(drop=True), ignore_index=True)
for a in range(100):
  for b in range(6):
    iter = str(a+1).zfill(3)
    programs_df = programs_df.append(pd.read_csv(f'../test/si_inc/t5_filtered_{iter}_00{b+1}.csv', index_col=0).reset_index(drop=True), ignore_index=True)
    programs_df = programs_df.append(pd.read_csv(f'../test/si_inv/t5_filtered_{iter}_00{b+1}.csv', index_col=0).reset_index(drop=True), ignore_index=True)

# %% Collapse into equivalent classes
all_pairs_df = pd.read_csv('../data/gen_pairs.csv', index_col=0)
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

eq_class_df.to_csv('test/all_eqc.csv')

# # %%
# incs = pd.read_csv('../for_exp/full_inc_eqc.csv', index_col=0)
# invs = pd.read_csv('../for_exp/full_inv_eqc.csv', index_col=0)
# total = pd.merge(incs, invs, how='outer', on='pred_list').fillna(value={"terms_x": '', "count_x": 0, "terms_y": '', "count_y": 0})
# total['count'] = total['count_x'] + total['count_y']
# total['merged_terms'] = total['terms_x'].where(total['terms_x']!='', total['terms_y'])
# total['compare_terms'] = total.apply(lambda row: len(row['terms_y'])-len(row['merged_terms']), axis=1)

# total_a = total[(total['merged_terms']!='')&(total['terms_y']!='')&(total['compare_terms']<0)]
# total_a['merged_terms'] = total['terms_y']
# total_b = total[~total.index.isin(total_a.index)]
# final = pd.concat([total_a, total_b], ignore_index=True)[['pred_list', 'merged_terms', 'count']].rename(columns={'merge_terms': 'terms'})

# final.to_csv('../for_exp/full_eqc.csv')
