
# %%
from pandas.core.common import flatten

# %% Global helper

# Get human-readable translation of a list of objects
# Expensive operation (recursion), be careful
def print_name(mylist):
  retlist = []
  for x in mylist:
    if isinstance(x, list):
      named_list = print_name(x)
      retlist.append(named_list)
    else:
      retlist.append(x.name)
  return retlist

# Return a list
def secure_list(input):
  output = input if isinstance(input, list) else [ input ]
  return output

# %% Define combinitorial logic terms

# base types
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

# objects
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

# primitives
class Primitive:
  ctype = 'primitive'
  def __init__(self, name = None, arg_type = None, return_type = None, func = None):
    self.name = name
    self.arg_type = arg_type
    self.return_type = return_type
    self.n_arg = len(list(flatten([arg_type])))
    self.run = func
  def __str__(self):
    return f'{self.name} {self.arg_type} -> {self.return_type}'

def get_color (obj):
  if isinstance(obj, list): obj = obj[0]
  return obj.color
getColor = Primitive('getColor', 'obj', 'col', get_color)

def set_color (arg_list):
  obj, col = arg_list
  obj.color = col
  return obj
setColor = Primitive('setColor', ['obj', 'col'], 'obj', set_color)

def eq_color(arg_list):
  col_1, col_2 = arg_list
  return col_1 == col_2
eqColor = Primitive('eqColor', ['col', 'col'], 'bool', eq_color)

def if_else(arg_list):
  cond, ret_1, ret_2 = arg_list
  return ret_1 if cond else ret_2
ifElse = Primitive('ifElse', ['bool', 'm', 'm'], 'obj', if_else) # m: program?

# routers
class Router:
  ctype = 'router'
  def __init__(self, name = None, func = None):
    self.name = name
    self.n_arg = len(name)
    self.run = func
  def __str__(self):
    return self.name

def send_right(arg_dict, arg_list):
  arg_dict['right'] = list(flatten(arg_dict['right'] + [arg_list]))
  return arg_dict
B = Router('B', send_right)

def send_left(arg_dict, arg_list):
  arg_dict['left'] = list(flatten(arg_dict['left'] + [arg_list]))
  return arg_dict
C = Router('C', send_left)

def send_both(arg_dict, arg_list):
  arg_dict['left'] = list(flatten(arg_dict['left'] + [arg_list]))
  arg_dict['right'] = list(flatten(arg_dict['right'] + [arg_list]))
  return arg_dict
S = Router('S', send_both)

def return_myself(arg_list):
  if isinstance(arg_list, list):
    return arg_list[0]
  else:
    return arg_list
I = Router('I', return_myself)

# composite routers
class ComRouter:
  ctype = 'router'
  def __init__(self, router_list):
    self.name = ''.join(list(map(lambda x: x.name, router_list)))
    self.n_arg = len(router_list)
    self.routers = router_list
  def run(self, arg_dict, arg_list):
    for i in range(len(self.routers)):
      self.routers[i].run(arg_dict, arg_list[i])
    return arg_dict
  def __str__(self):
    return self.name

# program
class Program:
  ctype = 'program'
  def __init__(self, terms):
    self.terms = terms
  def run(self, arg_list = None):
    if self.terms[0].ctype is 'router':
      if self.terms[0] is I:
        return I.run(arg_list)
      elif len(self.terms) != 3:
        print('Bad format!') # Raise error?
        return None
      else:
        router_term, left_terms, right_terms = self.terms
        left_tree = Program(secure_list(left_terms))
        right_tree = Program(secure_list(right_terms))
        # Route arguments
        sorted_args = {'left': [], 'right': []}
        sorted_args = router_term.run(sorted_args, arg_list)
        # Run subtrees
        left_ret = left_tree.run(sorted_args['left'])
        right_ret = right_tree.run(sorted_args['right'])
        return Program(secure_list(left_ret) + secure_list(right_ret)).run()
    elif self.terms[0].ctype is 'primitive': # TODO: include compound (learned) functions
      func_term = self.terms[0]
      args_term = self.terms[1:]
      if arg_list is not None:
        args_term += secure_list(arg_list)
      if len(args_term) == func_term.n_arg:
        return func_term.run(args_term) # Functions are leaf nodes
      else:
        return [ func_term ] + args_term
    else:
      return self.terms # Base types

# %% Run demo programs
s = Stone(Red, S2, Circle, S2, Plain, S1)
t = Stone(Blue, S1, Square, S4, Dotted, S2)

# demo = Program([C, setColor, Yellow])
# demo.run([s]).name

# BC = ComRouter([B,C])
# demo = Program([BC, setColor, getColor])
# demo.run([s, t]).name

# demo = Program([B, [eqColor, Red], getColor])
# demo.run(s)

CS = ComRouter([C, S])
CB = ComRouter([C, B])
demo = Program([CS, [CB, [B, ifElse, [B, [eqColor, Red], getColor]], [C, setColor, Red]], I])
demo.run([s, t]).name

# %%
# # %% Generate learning data
# learning_data = [
#   (Stone(Red, S2, Circle, S2, Plain, S1), Stone(Blue, S2, Circle, S2, Plain, S3), Stone(Red, S2, Circle, S2, Plain, S3)),
#   (Stone(Yellow, S2, Circle, S2, Plain, S1), Stone(Red, S1, Square, S2, Dotted, S1), Stone(Yellow, S1, Square, S2, Dotted, S1)),
#   (Stone(Red, S4, Circle, S2, Plain, S1), Stone(Blue, S4, Circle, S1, Plain, S4), Stone(Red, S4, Circle, S1, Plain, S4)),
#   (Stone(Blue, S1, Triangle, S2, Dotted, S4), Stone(Red, S4, Circle, S3, Plain, S4), Stone(Blue, S4, Circle, S3, Plain, S4))
# ]
