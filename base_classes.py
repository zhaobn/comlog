# %%
####################### General imports ###############################
from pandas.core.common import flatten

####################### Custom imports ###############################
from list_helpers import secure_list, copy_list

####################### Main body #####################################
class Color:
  ctype = 'col'
  def __init__(self, name): self.name = name
  def __str__(self): return self.name

class Shape:
  ctype = 'shp'
  def __init__(self, name): self.name = name
  def __str__(self): return self.name

class Pattern:
  ctype = 'pat'
  def __init__(self, name): self.name = name
  def __str__(self): return self.name

class Scale:
  ctype = 'int'
  def __init__(self, name): self.name = name
  def __str__(self): return str(self.name)

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
    if self.terms[0].ctype is 'router':
      if len(self.terms) is 1: # Should be router I
        return self.terms[0].run(arg_list)
      else:
        assert len(self.terms) == 3
        router_term, left_terms, right_terms = self.terms
        left_tree = Program(secure_list(left_terms))
        right_tree = Program(secure_list(right_terms))
        # Route arguments
        sorted_args = {'left': [], 'right': []}
        sorted_args = router_term.run(sorted_args, copy_list(arg_list))
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
