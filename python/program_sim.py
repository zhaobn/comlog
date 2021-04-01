# %%
import pandas as pd

from base_terms import *
from program_lib import Program_lib
from helpers import normalize, softmax

# %%
def get_pred(program_lib, partial_data, depth=3, type_sig=[['obj', 'obj'], 'obj']):
  pm_info = program_lib.generate_program(type_sig,max_step=depth)
  if 'ERROR' in pm_info['terms']:
    return None
  else:
    pm = Program(eval(pm_info['terms']))
    return pm.run([partial_data['agent'], partial_data['recipient']])
# get_pred(pl, data)

def sim_preds(partial_data, program_lib, n, softmax_base=0):
  ret_df = program_lib.get_all_objs()[['terms']]
  ret_df['count'] = 0
  for _ in range(n):
    result = get_pred(program_lib, partial_data)
    if result is not None:
      found_index = ret_df[ret_df['terms']==result.name].index.values[0]
      ret_df.at[found_index, 'count'] += 1
  ret_df['prob'] = normalize(ret_df['count']) if softmax_base == 0 else softmax(ret_df['count'], softmax_base)
  return ret_df
# sim_preds(data, pl, 100)

def sim_for_all(data_list, program_lib, n, softmax_base=0):
  ret_df = ret_df = program_lib.get_all_objs()[['terms']]
  for i in range(len(data_list)):
    preds = sim_preds(data_list[i], program_lib, n, softmax_base)
    preds = preds.rename(columns={"count": f"count_{i+1}", "prob": f"prob_{i+1}"})
    ret_df = pd.merge(ret_df, preds, on='terms', how='left')
  return ret_df

# # %%
# post_lib = pd.read_csv('data/test.csv', index_col=0, na_filter=False)
# pl = Program_lib(post_lib)

# sim_for_all([
#   {
#     'agent': Stone(Yellow,S2,Triangle,S1,Plain,S1),
#     'recipient': Stone(Yellow,S2,Square,S1,Dotted,S1)
#   },
#   {
#     'agent': Stone(Yellow,S2,Triangle,S1,Plain,S1),
#     'recipient': Stone(Red,S1,Triangle,S1,Plain,S1),
#   },
# ], pl, 5)
