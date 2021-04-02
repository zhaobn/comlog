# %%
####################### General imports ###############################
from pandas.core.common import flatten

####################### Custom imports ###############################
from helpers import secure_list, copy_list, print_name

####################### Main body #####################################
class Base:
  def __init__(self, ctype):
    self.ctype = ctype
  def __str__(self): return self.ctype

class Color(Base):
  def __init__(self, name):
    Base.__init__(self,'col')
    self.name = name
  def __str__(self): return self.name

class Shape(Base):
  def __init__(self, name):
    Base.__init__(self,'shp')
    self.name = name
  def __str__(self): return self.name

class Pattern:
  def __init__(self, name):
    Base.__init__(self,'pat')
    self.name = name
  def __str__(self): return self.name

class Scale:
  def __init__(self, name):
    Base.__init__(self,'int')
    self.name = name
  def __str__(self): return str(self.name)

class Stone:
  def __init__(self, color, c_scale, shape, s_scale, pattern, p_scale):
    Base.__init__(self,'obj')
    self.color = color
    self.saturation = c_scale
    self.shape = shape
    self.size = s_scale
    self.pattern = pattern
    self.density = p_scale
  @property
  def name(self): # Human-readable
    return f'Stone({self.color.name},{self.saturation.name},{self.shape.name},{self.size.name},{self.pattern.name},{self.density.name})'
  def __str__(self):
    return self.name

class Placeholder:
  ctype = 'placeholder'
  def __init__(self, name):
    self.name = name
  def __str__(self): return f'{self.name}'

class PM(Placeholder): # Programholder
  def __init__(self, type_sig, name='pgm'):
    Placeholder.__init__(self, name)
    types = type_sig.split('_')
    self.arg_types = '' if len(types) == 1 else types[:-1]
    self.return_type = types[-1]
  def __str__(self):
    return f'{self.name} {self.arg_types} -> {self.return_type}'

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

class Router:
  ctype = 'router'
  def __init__(self, name = None, func = None):
    self.name = name
    self.n_arg = len(name)
    self.run = func
  def __str__(self):
    return self.name

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

class Program:
  ctype = 'program'
  def __init__(self, terms):
    self.terms = terms
  def run(self, arg_list = None):
    if isinstance(self.terms[0], list):
      left_terms, right_terms = self.terms
      left_ret = Program(secure_list(left_terms)).run()
      right_ret = Program(secure_list(right_terms)).run()
      return Program(secure_list(left_ret) + secure_list(right_ret)).run()
    elif self.terms[0].ctype == 'router':
      if len(self.terms) == 1: # Should be router I
        return self.terms[0].run(arg_list)
      else:
        assert len(self.terms) == 3
        router_term, left_terms, right_terms = self.terms
        left_tree = Program(secure_list(left_terms))
        right_tree = Program(secure_list(right_terms))
        # Route arguments
        sorted_args = {'left': [], 'right': []}
        sorted_args = router_term.run(sorted_args, copy_list(secure_list(arg_list)))
        # Run subtrees
        left_ret = left_tree.run(sorted_args['left'])
        right_ret = right_tree.run(sorted_args['right'])
        return Program(secure_list(left_ret) + secure_list(right_ret)).run()
    elif self.terms[0].ctype == 'primitive': # TODO: include compound (learned) functions
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
