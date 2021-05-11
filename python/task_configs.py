# %%
import math
from copy import copy
from pandas.core.common import flatten

from helpers import secure_list, copy_list
from base_classes import Placeholder, Primitive, Program
from base_methods import if_else, send_right, send_left, send_both, constant, return_myself
from base_terms import B,C,S,K,BB,BC,BS,BK,CB,CC,CS,CK,SB,SC,SS,SK,KB,KC,KS,KK

# %% Define class
SHAPE_REF = {
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

class PM(Placeholder): # Programholder
  def __init__(self, type_sig, name='pgm'):
    Placeholder.__init__(self, name)
    types = type_sig.split('_')
    self.arg_types = '' if len(types) == 1 else types[:-1]
    self.return_type = types[-1]
  def __str__(self):
    return f'{self.name} {self.arg_types} -> {self.return_type}'

# %% Base terms
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


isTria = Primitive('isTria', ['obj'], 'bool', lambda x: x[0].shape.name=='Tria')
isRect = Primitive('isRect', ['obj'], 'bool', lambda x: x[0].shape.name=='Rect')
isPent = Primitive('isPent', ['obj'], 'bool', lambda x: x[0].shape.name=='Pent')
isHexa = Primitive('isHexa', ['obj'], 'bool', lambda x: x[0].shape.name=='Hexa')

isL1 = Primitive('isL1', ['obj'], 'bool', lambda x: x[0].length.name=='L1')
isL2 = Primitive('isL2', ['obj'], 'bool', lambda x: x[0].length.name=='L2')
isL3 = Primitive('isL3', ['obj'], 'bool', lambda x: x[0].length.name=='L3')
isL4 = Primitive('isL4', ['obj'], 'bool', lambda x: x[0].length.name=='L4')
isL5 = Primitive('isL5', ['obj'], 'bool', lambda x: x[0].length.name=='L5')
isL6 = Primitive('isL6', ['obj'], 'bool', lambda x: x[0].length.name=='L6')

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
  obj.length = Length(f'L{val}')
  return obj

def set_edge (arg_list):
  obj, val = arg_list
  v_index = list(SHAPE_REF.values()).index(val)
  if v_index > -1:
    obj.shape = eval(list(SHAPE_REF.keys())[v_index])
  return obj

getShape = Primitive('getShape', ['obj'], 'shape', lambda x: copy(x[0].shape.name))
setShape = Primitive('setShape', ['obj', 'shape'], 'obj', set_shape)

getEdge = Primitive('getEdge', ['obj'], 'num', lambda x: copy(x[0].shape.value))
setEdge = Primitive('setEdge', ['obj', 'num'], 'obj', set_edge)

getLength = Primitive('getLength', ['obj'], 'num', lambda x: copy(x[0].length.value))
setLength = Primitive('setLength', ['obj', 'num'], 'obj', set_length)

addnn = Primitive('addnn', ['num', 'num'], 'num', lambda x: sum(x))
mulnn = Primitive('mulnn', ['num', 'num'], 'num', lambda x: math.prod(x))

ifElse = Primitive('ifElse', ['bool', 'obj', 'obj'], 'obj', if_else)
I = Primitive('I', 'obj', 'obj', return_myself)

# %%
x = Stone(Tria,L1)
y = Stone(Rect,L1)
z = Program([BC,[B,setLength,I],[C,[B,addnn,[B,getEdge,I]],-1]]).run([x,y])
z.name

# %% Set up
# pm_task = clist_to_df([
#   White,Black,isWhite,isBlack,
#   Triangle,Square,Pentagon,Hexagon,isTriangle,isSquare,isPentagon,isHexagon,
#   S1,S2,S3,S4,S5,S6,S6,isS1,isS2,isS3,isS4,isS5,isS6,
#   getColor, setColor, eqColor,
#   getShape, setShape, eqShape,
#   getSize, setSize, eqSize,
#   getEdge,setEdge,eqEdge,
#   addVal,mulVal,ifElse,
#   {'terms': 'I', 'arg_types': 'obj', 'return_type': 'obj', 'type': 'program'},
#   True, False, 1,2,3,4,5,6
# ])
# pm_task.to_csv('data/pm_task.csv')
