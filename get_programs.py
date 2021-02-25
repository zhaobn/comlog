
# %%
import ast
import numpy as np
import pandas as pd
from pandas.core.common import random_state

from base_terms import *
from list_helpers import args_to_string, names_to_string

# Test pandas dataframe
df_pm = pd.DataFrame({
  'terms': [names_to_string(['C', 'setColor', 'Yellow'])],
  'arg_types': ['obj'],
  'return_type': ['obj'],
  'count': pd.Series([1], dtype='int32'),
  'name': ['']
})
# df_pm.to_csv('test.csv')
# df_pt = pd.read_csv('test.csv')
# ast.literal_eval(df_pt['terms'][0])[0]

# Add initial programs
programs_to_add = [ getColor, setColor, eqColor, eqObject, ifElse ]
for m in programs_to_add:
  df_pm = df_pm.append({
    'terms': names_to_string(secure_list(m.name)),
    'arg_types': args_to_string(m.arg_type),
    'return_type': m.return_type,
    'count': 1,
    'name': m.name
  }, ignore_index=True)

# %%
def get_cached_program(type_signature, p_source = df_pm):
  arg_t, ret_t = type_signature
  matched_pms = p_source.query(f'arg_types == "{args_to_string(arg_t)}" & return_type == "{ret_t}"')
  return matched_pms if not matched_pms.empty else None

def sample_program(p_source):
  sampled = p_source.sample(n=1, weights = 'count', random_state = 1)
  s_terms, s_arg_t, s_ret_t, = sampled.values[0][:3]
  return {'terms': s_terms, 'arg_types': s_arg_t, 'return_type': s_ret_t}

sample_program(get_cached_program([['obj'], 'obj']))

# %%
