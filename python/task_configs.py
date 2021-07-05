# %%
import math
from copy import copy
import pandas as pd
from pandas.core.common import flatten

from helpers import secure_list, copy_list
from base_classes import Placeholder, Primitive, Program
from base_methods import if_else, send_right, send_left, send_both, constant, return_myself
from base_terms import B,C,S,K,BB,BC,BS,BK,CB,CC,CS,CK,SB,SC,SS,SK,KB,KC,KS,KK

# %% Define class
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

class Length:
  def __init__(self, name):
    self.ctype = 'length'
    self.name = name
    self.value = int(name[1:])
  def __str__(self):
    return self.name

class Stone:
  def __init__(self, stripe, dot, length):
    self.ctype = 'obj'
    self.stripe = stripe
    self.dot = dot
    self.length = length
  @property
  def name(self):
    return f'Stone({self.stripe.name},{self.dot.name},{self.length.name})'
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
for i in range(5+1):
  exec(f"S{i} = Stripe('S{i}')")

for i in range(4+1):
  exec(f"O{i} = Dot('O{i}')")

for i in range(12+1):
  exec(f"L{i} = Length('L{i}')")

# Placeholders for typed program enumeration
stripe = Placeholder('stripe')
dot = Placeholder('dot')
length = Placeholder('length')
num = Placeholder('num')
obj = Placeholder('obj')

# %%
# Functional
def set_stripe (arg_list):
  obj, val = arg_list
  stripe_val = 0 if val < 0 else val
  obj.stripe = Stripe(f'S{stripe_val}')
  return obj

def set_dot (arg_list):
  obj, val = arg_list
  dot_val = 0 if val < 0 else val
  obj.dot = Stripe(f'O{dot_val}')
  return obj

def set_length (arg_list):
  obj, val = arg_list
  len_val = 1 if val < 1 else val
  obj.length = Length(f'L{len_val}')
  return obj

getStripe = Primitive('getStripe', ['obj'], 'num', lambda x: copy(x[0].stripe.value))
setStripe = Primitive('setStripe', ['obj', 'num'], 'obj', set_stripe)

getDot= Primitive('getDot', ['obj'], 'num', lambda x: copy(x[0].dot.value))
setDot= Primitive('setDot', ['obj', 'num'], 'obj', set_dot)

getLength = Primitive('getLength', ['obj'], 'num', lambda x: copy(x[0].length.value))
setLength = Primitive('setLength', ['obj', 'num'], 'obj', set_length)

addnn = Primitive('addnn', ['num', 'num'], 'num', lambda x: sum(x))
subnn = Primitive('subnn', ['num', 'num'], 'num', lambda x: x[0]-x[1])
mulnn = Primitive('mulnn', ['num', 'num'], 'num', lambda x: math.prod(x))

I = Primitive('I', 'obj', 'obj', return_myself)

# # %%
# x = Stone(S1,O0,L1)
# y = Stone(S0,O0,L2)
# z = Program([BC,[B,setLength,I],[C,[B,mulnn,[B,getStripe,I]],3]]).run([x,y])
# z.name

# # %% Task set up
# pm_setup = []
# pm_terms = [
#   S0, S1, S2, S3, S4,
#   O0, O1, O2, O3, O4,
#   L0, L1, L2, L3, L4, L5, L6, L7, L8, L9, L10, L11, L12,
#   1,2,3,
#   {'terms': '[B,I,I]', 'arg_types': 'obj', 'return_type': 'obj', 'type': 'program'},
#   {'terms': '[KB,I,I]', 'arg_types': 'obj_obj', 'return_type': 'obj', 'type': 'program'},
#   getStripe, getDot, getLength, setLength, #setStripe, setDot
#   addnn, subnn, mulnn, I,
# ]

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

# %%
