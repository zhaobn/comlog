# %%
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
Checkered = Pattern('Checkered')

S1 = Scale('S1')
S2 = Scale('S2')
S3 = Scale('S3')
S4 = Scale('S4')

# Placeholders for program enumeration
col = Placeholder('col')
shp = Placeholder('shp')
pat = Placeholder('pat')
int = Placeholder('int')
obj = Placeholder('obj')
pgm = Placeholder('pgm')
prm = Placeholder('prm')

# Primitives
# For bases
isRed = Primitive('isRed', ['obj'], 'bool', lambda x: x[0].color.name=='Red')
isYellow = Primitive('isYellow', ['obj'], 'bool', lambda x: x[0].color.name=='Yellow')
isBlue = Primitive('isBlue', ['obj'], 'bool', lambda x: x[0].color.name=='Blue')

isCircle = Primitive('isCircle', ['obj'], 'bool', lambda x: x[0].shape.name=='Circle')
isSquare = Primitive('isSquare', ['obj'], 'bool', lambda x: x[0].shape.name=='Square')
isTriangle = Primitive('isTriangle', ['obj'], 'bool', lambda x: x[0].shape.name=='Triangle')

isStripy = Primitive('isStripy', ['obj'], 'bool', lambda x: x[0].pattern.name=='Stripy')
isDotted = Primitive('isDotted', ['obj'], 'bool', lambda x: x[0].pattern.name=='Dotted')
isPlain = Primitive('isPlain', ['obj'], 'bool', lambda x: x[0].pattern.name=='Plain')
isCheckered = Primitive('isCheckered', ['obj'], 'bool', lambda x: x[0].pattern.name=='Checkered')

isS1Sat = Primitive('isS1Sat', ['obj'], 'bool', lambda x: x[0].saturation.name=='S1')
isS2Sat = Primitive('isS2Sat', ['obj'], 'bool', lambda x: x[0].saturation.name=='S2')
isS3Sat = Primitive('isS3Sat', ['obj'], 'bool', lambda x: x[0].saturation.name=='S3')
isS4Sat = Primitive('isS4Sat', ['obj'], 'bool', lambda x: x[0].saturation.name=='S4')

isS1Size = Primitive('isS1Size', ['obj'], 'bool', lambda x: x[0].size.name=='S1')
isS2Size = Primitive('isS2Size', ['obj'], 'bool', lambda x: x[0].size.name=='S2')
isS3Size = Primitive('isS3Size', ['obj'], 'bool', lambda x: x[0].size.name=='S3')
isS4Size = Primitive('isS4Size', ['obj'], 'bool', lambda x: x[0].size.name=='S4')

isS1Den = Primitive('isS1Den', ['obj'], 'bool', lambda x: x[0].density.name=='S1')
isS2Den = Primitive('isS2Den', ['obj'], 'bool', lambda x: x[0].density.name=='S2')
isS3Den = Primitive('isS3Den', ['obj'], 'bool', lambda x: x[0].density.name=='S3')
isS4Den = Primitive('isS4Den', ['obj'], 'bool', lambda x: x[0].density.name=='S4')

# Functional
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
# eqSaturation = Primitive('eqSaturation', ['int', 'int'], 'bool', eq_int)

getSize = Primitive('getSize', 'obj', 'int', get_size)
setSize = Primitive('setSize', ['obj', 'int'], 'obj', set_size)
# eqSize = Primitive('eqSize', ['int', 'int'], 'bool', eq_int)

getDensity = Primitive('getDensity', 'obj', 'int', get_density)
setDensity = Primitive('setDensity', ['obj', 'int'], 'obj', set_density)
# eqDensity = Primitive('eqDensity', ['int', 'int'], 'bool', eq_int)

eqInt = Primitive('eqInt', ['int', 'int'], 'bool', eq_int)
eqObject = Primitive('eqObject', [ 'obj', 'obj' ], 'bool', eq_object)
ifElse = Primitive('ifElse', ['bool', 'obj', 'obj'], 'obj', if_else)

I = Primitive('I', 'obj', 'obj', return_myself)

# Routers
B = Router('B', send_right)
C = Router('C', send_left)
S = Router('S', send_both)
# I = Router('I', return_myself)
K = Router('K', constant)

# Composite routers
BB = ComRouter([B, B])
BC = ComRouter([B, C])
BS = ComRouter([B, S])
BK = ComRouter([B, K])
CB = ComRouter([C, B])
CC = ComRouter([C, C])
CS = ComRouter([C, S])
CK = ComRouter([C, K])
SB = ComRouter([S, B])
SC = ComRouter([S, C])
SS = ComRouter([S, S])
SK = ComRouter([S, K])
KB = ComRouter([K, B])
KC = ComRouter([K, C])
KS = ComRouter([K, S])
KK = ComRouter([K, K])
