
####################### Custom imports ###############################
from base_classes import *
from base_methods import *

####################### Main body ###############################
# Base types
Red = Color('red')
Blue = Color('blue')
Yellow = Color('yellow')

Circle = Shape('circle')
Square = Shape('square')
Triangle = Shape('triangle')

Stripy = Pattern('stripy')
Dotted = Pattern('dotted')
Plain = Pattern('plain')

S1 = Scale(1)
S2 = Scale(2)
S3 = Scale(3)
S4 = Scale(4)

# Primitives
getColor = Primitive('getColor', 'obj', 'col', get_color)
setColor = Primitive('setColor', ['obj', 'col'], 'obj', set_color)
eqColor = Primitive('eqColor', ['col', 'col'], 'bool', eq_color)
eqObject = Primitive('eqObject', [ 'obj', 'obj' ], 'bool', eq_object)
ifElse = Primitive('ifElse', ['bool', 'm', 'm'], 'obj', if_else)

# Routers
B = Router('B', send_right)
C = Router('C', send_left)
S = Router('S', send_both)
I = Router('I', return_myself)

# Composite routers
BC = ComRouter([B,C])
CS = ComRouter([C, S])
CB = ComRouter([C, B])
