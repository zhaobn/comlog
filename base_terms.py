
####################### Custom imports ###############################
from base_classes import *
from base_methods import *

####################### Main body ###############################
# Base types
Red = Color('Red')
Blue = Color('Blue')
Yellow = Color('Yellow')

Circle = Shape('Circle')
Square = Shape('Square')
Triangle = Shape('Triangle')

Stripy = Pattern('Stripy')
Dotted = Pattern('Dotted')
Plain = Pattern('Plain')

S1 = Scale('S1')
S2 = Scale('S2')
S3 = Scale('S3')
S4 = Scale('S4')

# Primitives
getColor = Primitive('getColor', 'obj', 'col', get_color)
setColor = Primitive('setColor', ['obj', 'col'], 'obj', set_color)
eqColor = Primitive('eqColor', ['col', 'col'], 'bool', eq_color)
eqObject = Primitive('eqObject', [ 'obj', 'obj' ], 'bool', eq_object)
ifElse = Primitive('ifElse', ['bool', 'obj', 'obj'], 'obj', if_else)

# Routers
B = Router('B', send_right)
C = Router('C', send_left)
S = Router('S', send_both)
I = Router('I', return_myself)

# Composite routers
BB = ComRouter([B, B])
BC = ComRouter([B, C])
BS = ComRouter([B, S])
CB = ComRouter([C, B])
CC = ComRouter([C, C])
CS = ComRouter([C, S])
SB = ComRouter([S, B])
SC = ComRouter([S, C])
SS = ComRouter([S, S])
