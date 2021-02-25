
# %%
import ast
import numpy as np
import pandas as pd

from list_helpers import print_name, secure_list

from base_terms import *

# %% Test pandas dataframe
df_pm = pd.DataFrame({
  'terms': pd.Series([['C', 'setColor', 'Yellow']], dtype='object'),
  'arg_types': pd.Series([['obj']], dtype='object'),
  'return_type': ['obj'],
  'count': pd.Series([1], dtype='int32'),
  'name': ['']
})
# df_pm.to_csv('test.csv')
# df_pt = pd.read_csv('test.csv')
# ast.literal_eval(df_pt['terms'][0])[0]
# %% List of initial programs
programs_to_add = [ getColor, setColor, eqColor, eqObject, ifElse ]
for m in programs_to_add:
  df_pm = df_pm.append({
    'terms': secure_list(m.name),
    'arg_types': secure_list(m.arg_type),
    'return_type': m.return_type,
    'count': 1,
    'name': m.name
  }, ignore_index=True)

# %%
