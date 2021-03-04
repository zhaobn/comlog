
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

getShape = Primitive('getShape', 'obj', 'shp', get_shape)
setShape = Primitive('setShape', ['obj', 'shp'], 'obj', set_shape)
eqShape = Primitive('eqShape', ['shp', 'shp'], 'bool', eq_shape)

getPattern = Primitive('getPattern', 'obj', 'pat', get_pattern)
setPattern = Primitive('setPattern', ['obj', 'pat'], 'obj', set_pattern)
eqPattern = Primitive('eqPattern', ['pat', 'pat'], 'bool', eq_pattern)

getSaturation = Primitive('getSaturation', 'obj', 'int', get_saturation)
setSaturation = Primitive('setSaturation', ['obj', 'int'], 'obj', set_saturation)
eqSaturation = Primitive('eqSaturation', ['int', 'int'], 'bool', eq_saturation)

getSize = Primitive('getSize', 'obj', 'int', get_size)
setSize = Primitive('setSize', ['obj', 'int'], 'obj', set_size)
eqSize = Primitive('eqSize', ['int', 'int'], 'bool', eq_size)

getDensity = Primitive('getDensity', 'obj', 'int', get_density)
setDensity = Primitive('setDensity', ['obj', 'int'], 'obj', set_density)
eqDensity = Primitive('eqDensity', ['int', 'int'], 'bool', eq_density)

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
