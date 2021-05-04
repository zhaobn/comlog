
####################### General imports ###############################
from pandas.core.common import flatten
from copy import copy

####################### Main body #####################################
# Primitive functions
def get_color (obj):
  if isinstance(obj, list): obj = obj[0]
  return copy(obj.color)

def set_color (arg_list):
  obj, col = arg_list
  obj.color = copy(col)
  return obj

def eq_color(arg_list):
  col_1, col_2 = arg_list
  return col_1.name == col_2.name

def get_shape (obj):
  if isinstance(obj, list): obj = obj[0]
  return copy(obj.shape)

def set_shape (arg_list):
  obj, shp = arg_list
  obj.shape = copy(shp)
  return obj

def eq_shape(arg_list):
  shp_1, shp_2 = arg_list
  return shp_1.name == shp_2.name

def get_edge (obj):
  if isinstance(obj, list): obj = obj[0]
  return copy(obj.edge)

def set_edge (arg_list):
  obj, shp = arg_list
  obj.edge = copy(shp)
  return obj

def eq_edge(arg_list):
  shp_1, shp_2 = arg_list
  return shp_1.name == shp_2.name

def get_pattern (obj):
  if isinstance(obj, list): obj = obj[0]
  return copy(obj.pattern)

def set_pattern (arg_list):
  obj, pat = arg_list
  obj.pattern = copy(pat)
  return obj

def eq_pattern(arg_list):
  pat_1, pat_2 = arg_list
  return pat_1.name == pat_2.name

def get_saturation (obj):
  if isinstance(obj, list): obj = obj[0]
  return copy(obj.saturation)

def set_saturation (arg_list):
  obj, scl = arg_list
  obj.saturation = copy(scl)
  return obj

def get_size (obj):
  if isinstance(obj, list): obj = obj[0]
  return copy(obj.size)

def set_size (arg_list):
  obj, sz = arg_list
  obj.size = copy(sz)
  return obj

def get_density (obj):
  if isinstance(obj, list): obj = obj[0]
  return copy(obj.density)

def set_density (arg_list):
  obj, den = arg_list
  obj.density = copy(den)
  return obj

def eq_int(arg_list):
  int_1, int_2 = arg_list
  return int_1.name == int_2.name

def eq_object(arg_list):
  obj_1, obj_2 = arg_list
  return obj_1.name == obj_2.name

def if_else(arg_list):
  cond, ret_1, ret_2 = arg_list
  return ret_1 if cond else ret_2

# Router functions
def send_right(arg_dict, arg_list):
  arg_dict['right'] = list(flatten(arg_dict['right'] + [arg_list]))
  return arg_dict

def send_left(arg_dict, arg_list):
  arg_dict['left'] = list(flatten(arg_dict['left'] + [arg_list]))
  return arg_dict

def send_both(arg_dict, arg_list):
  arg_dict['left'] = list(flatten(arg_dict['left'] + [arg_list]))
  arg_dict['right'] = list(flatten(arg_dict['right'] + [arg_list]))
  return arg_dict

def return_myself(arg_list):
  if isinstance(arg_list, list):
    return arg_list[0]
  else:
    return arg_list

def constant(arg_dict, _):
  return arg_dict
