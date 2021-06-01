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
class Shape:
  def __init__(self, name):
    self.ctype = 'shape'
    self.name = name
    self.value = name
  def __str__(self):
    return self.name

class Length:
  def __init__(self, name):
    self.ctype = 'length'
    self.name = name
    self.value = int(name[1:])
  def __str__(self):
    return self.name

class Stripe:
  def __init__(self, name):
    self.ctype = 'stripe'
    self.name = name
    self.value = int(name[1:])
  def __str__(self):
    return self.name

class Stone:
  def __init__(self, shape, stripe, length):
    self.ctype = 'obj'
    self.shape = shape
    self.stripe = stripe
    self.length = length
  @property
  def name(self):
    return f'Stone({self.shape.name},{self.stripe.name},{self.length.name})'
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
Circ = Shape('Circ')
Rect = Shape('Rect')

for i in range(1,9+1):
  exec(f"L{i} = Length('L{i}')")

for i in range(5+1):
  exec(f"S{i} = Stripe('S{i}')")

# Placeholders for typed program enumeration
shape = Placeholder('shape')
stripe = Placeholder('stripe')
length = Placeholder('length')
num = Placeholder('num')
obj = Placeholder('obj')

# %%
# Functional
def set_shape (arg_list):
  obj, val = arg_list
  obj.shape = eval(str(copy(val)))
  return obj

def set_stripe (arg_list):
  obj, val = arg_list
  stripe_val = 0 if val < 0 else val
  obj.stripe = Stripe(f'S{stripe_val}')
  return obj

def set_length (arg_list):
  obj, val = arg_list
  len_val = 1 if val < 1 else val
  obj.length = Length(f'L{len_val}')
  return obj

getShape = Primitive('getShape', ['obj'], 'shape', lambda x: copy(x[0].shape))
setShape = Primitive('setShape', ['obj', 'shape'], 'obj', set_shape)

getStripe = Primitive('getStripe', ['obj'], 'num', lambda x: copy(x[0].stripe.value))
setStripe = Primitive('setStripe', ['obj', 'num'], 'obj', set_stripe)

getLength = Primitive('getLength', ['obj'], 'num', lambda x: copy(x[0].length.value))
setLength = Primitive('setLength', ['obj', 'num'], 'obj', set_length)

addnn = Primitive('addnn', ['num', 'num'], 'num', lambda x: sum(x))
mulnn = Primitive('mulnn', ['num', 'num'], 'num', lambda x: math.prod(x))

I = Primitive('I', 'obj', 'obj', return_myself)

# # %%
# x = Stone(Circ,S1,L1)
# y = Stone(Rect,S0,L2)
# z = Program([BC,[B,setLength,I],[C,[B,mulnn,[B,getStripe,I]],3]]).run([x,y])
# z.name

# %% Task set up
pm_setup = []
pm_terms = [
  Circ, Rect,
  S0, S1, S2, S3, S4, S5,
  L1, L2, L3, L4, L5, L6, L7, L8, L9,
  getShape, setShape, getStripe, setStripe, getLength, setLength,
  addnn, mulnn, I,
]

for pt in pm_terms:
  if isinstance(pt, bool) or isinstance(pt, int):
    terms = str(pt)
    arg_types = ''
    return_type = 'bool' if isinstance(pt, bool) else 'num'
    type = 'base_term'
  elif pt.ctype == 'shape' or pt.ctype == 'length' or pt.ctype == 'stripe':
    terms = pt.name
    arg_types = ''
    return_type = pt.ctype
    type = 'base_term'
  else:
    terms = pt.name
    arg_types = '_'.join(secure_list(pt.arg_type))
    return_type = pt.return_type
    type = 'primitive'
  pm_setup.append({'terms':terms,'arg_types':arg_types,'return_type':return_type,'type':type,'count':1})

pm_task = (pd.DataFrame.from_records(pm_setup)
  .groupby(by=['terms','arg_types','return_type','type'], as_index=False)
  .agg({'count': pd.Series.count})
  .sort_values(by=['type','return_type','arg_types','terms'])
  .reset_index(drop=1))
pm_task.to_csv('data/task_pm.csv') # Later manually add [KB,I,I] & [B,I,I]

# %%
