
# %%
import pandas as pd
pd.set_option('mode.chained_assignment', None)

from base_terms import *
from helpers import term_to_dict
from program_generator import Program_lib, data

# %% Basic setup
pms = pd.read_csv('data/rc_cp.csv', index_col=0)

# pm_init = pd.read_csv('data/pm_init.csv',index_col=0, na_filter=False)
# pl = Program_lib(pm_init)

# %%
def extract_programs(terms):
  df = pd.DataFrame({'terms': [], 'arg_types': [], 'return_type': [], 'type': [], 'count': []})
  if isinstance(terms, str):
    terms = eval(terms)
  for t in terms:
    if isinstance(t, bool) != 1:
      if t.ctype in pl.SET_MARKERS:
        base_df.at[base_df[base_df.terms==t].index.values[0], 'count'] += 1
      # elif c.type == 'obj':
      #   base_df.at[base_df[base_df.terms==t].index.values[0], 'count'] += 1
  return base_df

# %%


test = Program_lib_light(pd.DataFrame({'terms': [], 'arg_types': [], 'return_type': [], 'type': [], 'count': []}))
test.add([Red, Red, True])

# %%
