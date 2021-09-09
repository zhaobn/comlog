# %%
import math
from copy import copy
import pandas as pd
from pandas.core.common import flatten

from helpers import secure_list, copy_list
from base_classes import Placeholder, Primitive, Program
from base_methods import if_else, send_right, send_left, send_both, constant, return_myself
from base_terms import B,C,S,K,BB,BC,BS,BK,CB,CC,CS,CK,SB,SC,SS,SK,KB,KC,KS,KK

# %%
# Classes
class Stripe:
  def __init__(self, name):
    self.ctype = 'stripe'
    self.name = name
    self.value = int(name[1:])
  def __str__(self):
    return self.name

class Dot:
  def __init__(self, name):
    self.ctype = 'dot'
    self.name = name
    self.value = int(name[1:])
  def __str__(self):
    return self.name

class Egg:
  def __init__(self, stripe, dot):
    self.ctype = 'egg'
    self.stripe = stripe
    self.dot = dot
  @property
  def name(self):
    return f'Egg({self.stripe.name},{self.dot.name})'
  def __str__(self):
    return self.name

class PM(Placeholder): # Programholder for typed enumeration
  def __init__(self, type_sig, name='pgm'):
    Placeholder.__init__(self, name)
    types = type_sig.split('_')
    self.arg_types = '' if len(types) == 1 else types[:-1]
    self.return_type = types[-1]
  def __str__(self):
    return f'{self.name} {self.arg_types} -> {self.return_type}'

# Base terms
for i in range(5):
  exec(f"S{i} = Stripe('S{i}')")

for i in range(5):
  exec(f"O{i} = Dot('O{i}')")

# Placeholders for typed program enumeration
stripe = Placeholder('stripe')
dot = Placeholder('dot')
num = Placeholder('num')
egg = Placeholder('egg')

# Primitives
getStripe = Primitive('getStripe', ['egg'], 'num', lambda x: copy(x[0].stripe.value))
getDot= Primitive('getDot', ['egg'], 'num', lambda x: copy(x[0].dot.value))

addnn = Primitive('addnn', ['num', 'num'], 'num', lambda x: sum(x))
subnn = Primitive('subnn', ['num', 'num'], 'num', lambda x: x[0]-x[1])
mulnn = Primitive('mulnn', ['num', 'num'], 'num', lambda x: math.prod(x))

I = Primitive('I', 'egg', 'egg', return_myself)

# # %% Debug
# x = Egg(S2,O0)
# y = 4
# Program([CB,[B,mulnn,getStripe],I]).run([x,y])

# # %% Task set up
# pm_terms = list(range(5)) + [
#   S0, S1, S2, S3, S4,
#   O0, O1, O2, O3, O4,
#   getStripe, getDot, addnn, subnn, mulnn, I,
#   {'terms': '[B,I,I]', 'arg_types': 'num', 'return_type': 'num', 'type': 'program'},
#   {'terms': '[KB,I,I]', 'arg_types': 'egg_num', 'return_type': 'num', 'type': 'program'},
#   {'terms': '[BK,I,I]', 'arg_types': 'egg_num', 'return_type': 'egg', 'type': 'program'},
# ]

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
# pm_task.to_csv('data/task_pm.csv')

# %%
