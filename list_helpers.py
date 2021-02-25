
####################### General imports ###############################
from copy import copy


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

# Return copy of a list (of objects)
def copy_list(lt):
  ret = []
  for _l in lt: ret.append(copy(_l))
  return ret
