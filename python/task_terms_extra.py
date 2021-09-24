# %%
import math
import pandas as pd
from pandas.core.common import flatten
from copy import copy

from helpers import secure_list, copy_list
from task_terms import *
# from program_lib import Program_lib

# %%
# Placeholders for typed program enumeration
bol = Placeholder('bol')

# Primitives
moreDots = Primitive('moreDots', ['egg'], 'bol', lambda x: x[0].dot.value > x[0].stripe.value)
equalDots = Primitive('equalDots', ['egg'], 'bol', lambda x: x[0].dot.value == x[0].stripe.value)
lessDots = Primitive('lessDots', ['egg'], 'bol', lambda x: x[0].dot.value < x[0].stripe.value)

def if_else(arg_list):
  cond, ret_1, ret_2 = arg_list
  return ret_1 if cond else ret_2
ifElse = Primitive('ifElse', ['bol', 'num', 'num'], 'num', if_else)

# %% Debug
# x = Egg(S1,O2)
# equalDots.run([x])
# y = 4
# Program([CB,[S,[B,ifElse,moreDots],getStripe],[B,I,I]]).run([x,y])

# # %% Task set up
# pm_terms = [
#   moreDots, equalDots, lessDots, ifElse,
#   {'terms': 'numBol', 'arg_types': 'num', 'return_type': 'bol', 'type': 'primitive'},
#   {'terms': 'baseBol', 'arg_types': '', 'return_type': 'bol', 'type': 'base_term'},
#  ]

# pm_setup = []
# for pt in pm_terms:
#   if isinstance(pt, dict):
#     terms = pt['terms']
#     arg_types = pt['arg_types']
#     return_type = pt['return_type']
#     type = pt['type']
#   elif isinstance(pt, bool) or isinstance(pt, int):
#     terms = str(pt)
#     arg_types = ''
#     return_type = 'bool' if isinstance(pt, bool) else 'num'
#     type = 'base_term'
#   elif pt.ctype == 'dot' or pt.ctype == 'length' or pt.ctype == 'stripe':
#     terms = pt.name
#     arg_types = ''
#     return_type = pt.ctype
#     type = 'base_term'
#   else:
#     terms = pt.name
#     arg_types = '_'.join(secure_list(pt.arg_type))
#     return_type = pt.return_type
#     type = 'primitive'
#   pm_setup.append({'terms':terms,'arg_types':arg_types,'return_type':return_type,'type':type,'count':1})

# pm_task = (pd.DataFrame.from_records(pm_setup)
#   .groupby(by=['terms','arg_types','return_type','type'], as_index=False)
#   .agg({'count': pd.Series.count})
#   .sort_values(by=['type','return_type','arg_types','terms'])
#   .reset_index(drop=1))
# pm_task['is_init'] = int(1)

# base_pms = pd.read_csv('data/task_pm.csv', index_col=0, na_filter=False)
# pm_extended = pd.concat([base_pms, pm_task], ignore_index=True)

# pme = Program_lib(pm_extended[['terms','arg_types','return_type','type','is_init','count']])
# pme.initial_comp_lp()
# pme.update_lp_adaptor()
# pme.update_overall_lp()
# pme.content.to_csv('data/task_pm_extended.csv')

# %%
