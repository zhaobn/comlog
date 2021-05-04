# %%
import math
from copy import copy

from task_configs import *
from base_classes import Placeholder, Primitive, Program
from base_methods import if_else, send_right, send_left, send_both, constant, return_myself
from base_terms import B,C,S,K,BB,BC,BS,BK,CB,CC,CS,CK,SB,SC,SS,SK,KB,KC,KS,KK
# from program_lib import *

# %% Base terms
Black = Color('Black')
White = Color('White')

Triangle = Shape('Triangle')
Square = Shape('Square')
Pentagon = Shape('Pentagon')
Hexagon = Shape('Hexagon')

S1 = Size('S1')
S2 = Size('S2')
S3 = Size('S3')
S4 = Size('S4')
S5 = Size('S5')
S6 = Size('S6')

isBlack = Primitive('isBlack',['obj'],'bool',lambda x: x[0].color.name=='Black')
isWhite = Primitive('isWhite',['obj'],'bool',lambda x: x[0].color.name=='White')

isTriangle = Primitive('isTriangle', ['obj'], 'bool', lambda x: x[0].shape.name=='Triangle')
isSquare = Primitive('isSquare', ['obj'], 'bool', lambda x: x[0].shape.name=='Square')
isPentagon = Primitive('isPentagon', ['obj'], 'bool', lambda x: x[0].shape.name=='Pentagon')
isHexagon = Primitive('isHexagon', ['obj'], 'bool', lambda x: x[0].shape.name=='Hexagon')

isS1 = Primitive('isS1', ['obj'], 'bool', lambda x: x[0].size.name=='S1')
isS2 = Primitive('isS2', ['obj'], 'bool', lambda x: x[0].size.name=='S2')
isS3 = Primitive('isS3', ['obj'], 'bool', lambda x: x[0].size.name=='S3')
isS4 = Primitive('isS4', ['obj'], 'bool', lambda x: x[0].size.name=='S4')
isS5 = Primitive('isS5', ['obj'], 'bool', lambda x: x[0].size.name=='S5')
isS6 = Primitive('isS6', ['obj'], 'bool', lambda x: x[0].size.name=='S6')

# Placeholders for typed program enumeration
color = Placeholder('color')
shape = Placeholder('shape')
num = Placeholder('num')
obj = Placeholder('obj')

# Functional
def set_color (arg_list):
  obj, val = arg_list
  obj.color = eval(str(copy(val)))
  return obj

def set_shape (arg_list):
  obj, val = arg_list
  obj.shape = eval(str(copy(val)))
  return obj

def set_size (arg_list):
  obj, val = arg_list
  ref = Size('S1').ref
  upper_bound = max(list(ref.values()))
  lower_bound= min(list(ref.values()))
  if val > upper_bound:
    val = copy(upper_bound)
  elif val < lower_bound:
    val = copy(lower_bound)
  else:
    val = copy(val)
  size_name = list(ref.keys())[list(ref.values()).index(val)]
  obj.size = eval(size_name)
  return obj

def set_edge (arg_list):
  obj, val = arg_list
  ref = Shape('Square').ref
  upper_bound = max(list(ref.values()))
  lower_bound= min(list(ref.values()))
  if val > upper_bound:
    val = copy(upper_bound)
  elif val < lower_bound:
    val = copy(lower_bound)
  else:
    val = copy(val)
  shape_name = list(ref.keys())[list(ref.values()).index(val)]
  obj.shape = eval(shape_name)
  return obj

getColor = Primitive('getColor', ['obj'], 'color', lambda x: copy(x[0].color.name))
setColor = Primitive('setColor', ['obj', 'color'], 'obj', set_color)
eqColor = Primitive('eqColor', ['color', 'color'], 'bool', lambda x: x[0].color.name==x[1].color.name)

getShape = Primitive('getShape', ['obj'], 'shape', lambda x: copy(x[0].shape.name))
setShape = Primitive('setShape', ['obj', 'shape'], 'obj', set_shape)
eqShape = Primitive('eqShape', ['shape', 'shape'], 'bool', lambda x: x[0].shape.name==x[1].shape.name)

getEdge = Primitive('getEdge', ['obj'], 'num', lambda x: copy(x[0].shape.value))
setEdge = Primitive('setEdge', ['obj', 'num'], 'obj', set_edge)
eqEdge = Primitive('eqEdge', ['num', 'num'], 'bool', lambda x: x[0].shape.value==x[1].shape.value)

getSize = Primitive('getSize', ['obj'], 'num', lambda x: copy(x[0].size.value))
setSize = Primitive('setSize', ['obj', 'num'], 'obj', set_size)
eqSize = Primitive('eqSize', ['size', 'num'], 'bool', lambda x: x[0].size.value==x[1].size.value)

addVal = Primitive('addVal', ['num', 'num'], 'num', lambda x: sum(x))
mulVal = Primitive('mulVal', ['num', 'num'], 'num', lambda x: math.prod(x))

qObject = Primitive('eqObject', ['obj', 'obj'], 'bool', lambda x: x[0].name==x[1].name)
ifElse = Primitive('ifElse', ['bool', 'obj', 'obj'], 'obj', if_else)

I = Primitive('I', 'obj', 'obj', return_myself)


# %%
x = Stone(White,Square,S4)
y = Stone(Black,Square,S3)
z = Program([BS,[B,setSize,I],[BC,[B,addVal,[B,getSize,I]],[B,getEdge,I]]]).run([x,y])
z.name
