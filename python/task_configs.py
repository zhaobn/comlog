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
SHAPE_REF = {
  'Snil': 0,
  'Tria': 3,
  'Rect': 4,
  'Pent': 5,
  'Hexa': 6,
  'Hept': 7,
}
class Shape:
  def __init__(self, name):
    self.ctype = 'shape'
    self.name = name
    self.value = SHAPE_REF[name]
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
  def __init__(self, shape, length):
    self.ctype = 'obj'
    self.shape = shape
    self.length = length
  @property
  def name(self):
    return f'Stone({self.shape.name},{self.length.name})'
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
Snil = Shape('Snil')
Tria = Shape('Tria')
Rect = Shape('Rect')
Pent = Shape('Pent')
Hexa = Shape('Hexa')

L1 = Length('L1')
L2 = Length('L2')
L3 = Length('L3')
L4 = Length('L4')
L5 = Length('L5')
L6 = Length('L6')
# L7 = Length('L7')


# Placeholders for typed program enumeration
shape = Placeholder('shape')
length = Placeholder('length')
num = Placeholder('num')
obj = Placeholder('obj')

# Functional
def set_shape (arg_list):
  obj, val = arg_list
  obj.shape = eval(str(copy(val)))
  return obj

def set_length (arg_list):
  obj, val = arg_list
  len_val = 1 if val < 1 else val
  obj.length = Length(f'L{len_val}')
  return obj

def set_edge (arg_list):
  obj, val = arg_list
  edge_val = 0 if val < 3 or val > 5 else val
  v_index = list(SHAPE_REF.values()).index(edge_val)
  obj.shape = eval(list(SHAPE_REF.keys())[v_index])
  return obj

getShape = Primitive('getShape', ['obj'], 'shape', lambda x: copy(x[0].shape))
setShape = Primitive('setShape', ['obj', 'shape'], 'obj', set_shape)
isShape = Primitive('isShape', ['obj', 'shape'], 'bool', lambda x: x[0].shape.name==x[1].name)

getEdge = Primitive('getEdge', ['obj'], 'num', lambda x: copy(x[0].shape.value))
setEdge = Primitive('setEdge', ['obj', 'num'], 'obj', set_edge)

getLength = Primitive('getLength', ['obj'], 'num', lambda x: copy(x[0].length.value))
setLength = Primitive('setLength', ['obj', 'num'], 'obj', set_length)
isLength = Primitive('isLength', ['obj', 'num'], 'bool', lambda x: x[0].length.value==x[1])

addnn = Primitive('addnn', ['num', 'num'], 'num', lambda x: sum(x))
mulnn = Primitive('mulnn', ['num', 'num'], 'num', lambda x: math.prod(x))

ifElse = Primitive('ifElse', ['bool', 'obj', 'obj'], 'obj', if_else)
I = Primitive('I', 'obj', 'obj', return_myself)

isTria = Primitive('isTria', ['obj'], 'bool', lambda x: x[0].shape.name=='Tria')
isRect = Primitive('isRect', ['obj'], 'bool', lambda x: x[0].shape.name=='Rect')
isPent = Primitive('isPent', ['obj'], 'bool', lambda x: x[0].shape.name=='Pent')
# isL1 = Primitive('isL1', ['obj'], 'bool', lambda x: x[0].length.name=='L1')
# isL2 = Primitive('isL2', ['obj'], 'bool', lambda x: x[0].length.name=='L2')
# isL3 = Primitive('isL3', ['obj'], 'bool', lambda x: x[0].length.name=='L3')

# # %%
# x = Stone(Pent,L1)
# y = Stone(Rect,L1)
# z = Program([BC,[B,setLength,I],[C,[B,mulnn,[B,getEdge,I]],2]]).run([x,y])
# z.name

# # %% Task set up
# pm_setup = []
# pm_terms = [
#   Tria, Rect, Pent, Hexa, isTria, isRect, isPent,
#   L1, L2, L3, L4, L5, L6, #L7, isL1, isL2, isL3,
#   getShape, setShape, getEdge, setEdge, getLength, setLength, isShape, isLength,
#   addnn, mulnn, ifElse, I,
#   -2, -1, 0, 1, 2, True, False,
# ]
# for pt in pm_terms:
#   if isinstance(pt, bool) or isinstance(pt, int):
#     terms = str(pt)
#     arg_types = ''
#     return_type = 'bool' if isinstance(pt, bool) else 'num'
#     type = 'base_term'
#   elif pt.ctype == 'shape' or pt.ctype == 'length':
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

# pm_task = pd.DataFrame.from_records(pm_setup).groupby(by=['terms','arg_types','return_type','type'], as_index=False).agg({'count': pd.Series.count})
# pm_task.to_csv('data/task_pm.csv') # Later manually add [KB,I,I] & [B,I,I]

# %%
