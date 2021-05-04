# %%
from base_classes import Color, Scale, Placeholder, Primitive, Program
from base_methods import *
from base_terms import B,C,S,K,BB,BC,BS,BK,CB,CC,CS,CK,SB,SC,SS,SK,KB,KC,KS,KK
from program_lib import *

# %%
class Stone:
  def __init__(self, color, edge, size):
    Base.__init__(self,'obj')
    self.color = color
    self.edge = edge
    self.size = size
  @property
  def name(self):
    return f'Stone({self.color.name},{self.edge.name},{self.size.name})'
  def __str__(self):
    return self.name

Black = Color('Black')
White = Color('White')

E3 = Scale('E3')
E4 = Scale('E4')
E5 = Scale('E5')

S1 = Scale('S1')
S2 = Scale('S2')
S3 = Scale('S3')
S5 = Scale('S5')
S6 = Scale('S6')

isBlack = Primitive('isBlack',['obj'],'bool',lambda x: x[0].color.name=='Black')
isWhite = Primitive('isWhite',['obj'],'bool',lambda x: x[0].color.name=='White')

isE3 = Primitive('isE3', ['obj'], 'bool', lambda x: x[0].edge.name=='E3')
isE4 = Primitive('isE4', ['obj'], 'bool', lambda x: x[0].edge.name=='E4')
isE5 = Primitive('isE5', ['obj'], 'bool', lambda x: x[0].edge.name=='E5')

isS1 = Primitive('isS1', ['obj'], 'bool', lambda x: x[0].size.name=='S1')
isS2 = Primitive('isS2', ['obj'], 'bool', lambda x: x[0].size.name=='S2')
isS3 = Primitive('isS3', ['obj'], 'bool', lambda x: x[0].size.name=='S3')
isS4 = Primitive('isS4', ['obj'], 'bool', lambda x: x[0].size.name=='S4')
isS5 = Primitive('isS5', ['obj'], 'bool', lambda x: x[0].size.name=='S5')
isS6 = Primitive('isS6', ['obj'], 'bool', lambda x: x[0].size.name=='S6')

# Placeholders for typed program enumeration
Col = Placeholder('Col')
Int = Placeholder('Int')

# Functional
getColor = Primitive('getColor', 'obj', 'col', get_color)
setColor = Primitive('setColor', ['obj', 'col'], 'obj', set_color)
eqColor = Primitive('eqColor', ['col', 'col'], 'bool', eq_color)

getEdge = Primitive('getEdge', 'obj', 'shp', get_edge)
setEdge = Primitive('setEdge', ['obj', 'shp'], 'obj', set_edge)
eqEdge = Primitive('eqEdge', ['shp', 'shp'], 'bool', eq_edge)

getSize = Primitive('getSize', 'obj', 'int', get_size)
setSize = Primitive('setSize', ['obj', 'int'], 'obj', set_size)
eqSize = Primitive('eqSize', ['int', 'int'], 'bool', eq_int)

eqInt = Primitive('eqInt', ['int', 'int'], 'bool', eq_int)
eqObject = Primitive('eqObject', [ 'obj', 'obj' ], 'bool', eq_object)
ifElse = Primitive('ifElse', ['bool', 'obj', 'obj'], 'obj', if_else)

I = Primitive('I', 'obj', 'obj', return_myself)

# %%
