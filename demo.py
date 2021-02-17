
# %% Define base types
class Color:
  ctype = 'col'
  def __init__(self, val): self.val = val
  def __str__(self): return self.val

Red = Color('red')
Blue = Color('blue')
Yellow = Color('yellow')

class Shape:
  ctype = 'shp'
  def __init__(self, val): self.val = val
  def __str__(self): return self.val

Circle = Shape('circle')
Square = Shape('square')
Triangle = Shape('triangle')

class Pattern:
  ctype = 'pat'
  def __init__(self, val): self.val = val
  def __str__(self): return self.val

Stripy = Pattern('stripy')
Dotted = Pattern('dotted')
Plain = Pattern('plain')

class Scale:
  ctype = 'int'
  def __init__(self, val): self.val = val
  def __str__(self): return str(self.val)

S1 = Scale(1)
S2 = Scale(2)
S3 = Scale(3)
S4 = Scale(4)

# %% Define objects
class Stone:
  ctype = 'obj'
  def __init__(self, color = None, c_scale = None, shape = None, s_scale = None, pattern = None, p_scale = None):
    self.col = color.val
    self.col_int = c_scale.val
    self.shp = shape.val
    self.shp_int = s_scale.val
    self.pat = pattern.val
    self.pat_int = p_scale.val
  def __str__(self):
    return f'{self.col}{self.col_int}_{self.shp}{self.shp_int}_{self.pat}{self.pat_int}'

# s = Stone(Red, S2, Circle, S2, Plain, S1)

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
    self.run = func
  def __str__(self):
    return f'{self.name} {self.typesig}'

def get_color (obj):
  return obj.col
getColor = Primitive('getColor', ['obj', 'col'], get_color)

def set_color (obj, col):
  obj.col = col
  return obj
setColor = Primitive('setColor', ['obj', ['obj', 'col']], set_color)

# %% Routers
class Router:
  ctype = 'router'
  def __init__(self, name = None, func = None):
    self.name = name
    self.run = func
  def __str__(self):
    return f'{self.name}'

def send_right(x, y, z):
  return [ y, z(x) ]
B = Router('B', send_right)

def send_left(x, y, z):
  return [ y(x), z ]
C = Router('C', send_left)

def send_both(x, y, z):
  return [ y(x), z(x) ]
S = Router('S', send_both)

# %%
