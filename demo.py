
# %%
from pandas.core.common import flatten, is_true_slices

# %% Define base types
class Color:
  ctype = 'col'
  def __init__(self, name): self.name = name
  def __str__(self): return self.name

Red = Color('red')
Blue = Color('blue')
Yellow = Color('yellow')

class Shape:
  ctype = 'shp'
  def __init__(self, name): self.name = name
  def __str__(self): return self.name

Circle = Shape('circle')
Square = Shape('square')
Triangle = Shape('triangle')

class Pattern:
  ctype = 'pat'
  def __init__(self, name): self.name = name
  def __str__(self): return self.name

Stripy = Pattern('stripy')
Dotted = Pattern('dotted')
Plain = Pattern('plain')

class Scale:
  # For now: same scale for all three categorical features;
  # Future: consider different scale per categorical feature.
  ctype = 'int'
  def __init__(self, name): self.name = name
  def __str__(self): return str(self.name)

S1 = Scale(1)
S2 = Scale(2)
S3 = Scale(3)
S4 = Scale(4)

# %% Define objects
class Stone:
  ctype = 'obj'
  def __init__(self, color, c_scale, shape, s_scale, pattern, p_scale):
    self.color = color
    self.saturation = c_scale
    self.shape = shape
    self.size = s_scale
    self.pattern = pattern
    self.density = p_scale
  @property
  def name(self): # Human-readable
    return (
      self.color.name + str(self.saturation.name) + '_'
      + self.shape.name + str(self.size.name) + '_'
      + self.pattern.name + str(self.density.name))
  def __str__(self):
    return self.name

s = Stone(Red, S2, Circle, S2, Plain, S1)

# %% Generate learning data
learning_data = [
  (Stone(Red, S2, Circle, S2, Plain, S1), Stone(Blue, S2, Circle, S2, Plain, S3), Stone(Red, S2, Circle, S2, Plain, S3)),
  (Stone(Yellow, S2, Circle, S2, Plain, S1), Stone(Red, S1, Square, S2, Dotted, S1), Stone(Yellow, S1, Square, S2, Dotted, S1)),
  (Stone(Red, S4, Circle, S2, Plain, S1), Stone(Blue, S4, Circle, S1, Plain, S4), Stone(Red, S4, Circle, S1, Plain, S4)),
  (Stone(Blue, S1, Triangle, S2, Dotted, S4), Stone(Red, S4, Circle, S3, Plain, S4), Stone(Blue, S4, Circle, S3, Plain, S4))
]

# %% Primitives
class Primitive:
  ctype = 'primitive'
  def __init__(self, name = None, typesig = [], func = None):
    self.name = name
    self.typesig = typesig
    self.run = func # Handcrafted for now; not sure how to make it automatically defined by type signature
  def __str__(self):
    return f'{self.name} {self.typesig}'

def get_color (obj): return obj.color
getColor = Primitive('getColor', ['obj', 'col'], get_color)

def set_color (obj, col): obj.color = col; return obj
setColor = Primitive('setColor', ['obj', ['obj', 'col']], set_color)

# %% Routers
class Router:
  ctype = 'router'
  def __init__(self, name = None, func = None):
    self.name = name
    self.run = func
    self.n_var = len(name)
  def __str__(self):
    return self.name

def send_right(x, y, z): return [ x, [y, z] ]
B = Router('B', send_right)

def send_left(x, y, z): return [[ x, z ], y ]
C = Router('C', send_left)

def send_both(x, y, z): return [ x, z, [ y, z ]]
S = Router('S', send_both)

def return_myself(x): return x
I = Router('I', return_myself)

# %% Composite routers
class ComRouter:
  ctype = 'router'
  def __init__(self, routers):
    self.name = ''.join(list(map(lambda x: x.name, routers)))
    self.n_var = len(routers)
    self.routers = routers
  def __str__(self):
    return self.name

BC = ComRouter([B, C])

# %% Demo program
class Program:
  ctype = 'program'
  def __init__(self, terms):
    self.terms = terms
  def print_program(self):
    def recursive_get_name(mylist):
	    retlist = []
	    for x in mylist:
		    if isinstance(x, list):
			    named_list = recursive_get_name(x)
			    retlist.append(named_list)
		    else:
			    retlist.append(x.name)
	    return retlist
    return recursive_get_name(self.terms)

demo = Program([BC, setColor, getColor])
simple_demo = Program([C, setColor, Yellow])

# %%
def runProgram(program, objs):


# %%
t = Stone(Blue, S1, Circle, S2, Dotted, S2)
