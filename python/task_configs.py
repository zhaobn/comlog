# %%
from copy import copy
from pandas.core.common import flatten
from helpers import secure_list, copy_list

# %%
class Base:
  def __init__(self, ctype, name, ref):
    self.ctype = ctype
    self.name = name
    self.ref = ref
  @property
  def value(self):
    return self.ref[self.name]

class Color(Base):
  def __init__(self, name):
    Base.__init__(self, 'color', name, {
      'White': 0,
      'Black': 1,
    })
class Shape(Base):
  def __init__(self, name):
    Base.__init__(self, 'shape', name, {
      'Triangle': 1,
      'Square': 2,
      'Pentagon': 3,
      'Hexagon': 4,
    })

class Size(Base):
  size_ref = {}
  for i in range(1,7):
    size_ref[f'S{str(i)}'] = i
  def __init__(self, name):
    Base.__init__(self, 'size', name, self.size_ref)

class Stone:
  def __init__(self, color, shape, size):
    self.ctype = 'obj'
    self.color = color
    self.shape = shape
    self.size = size
  @property
  def name(self):
    return f'Stone({self.color.name},{self.shape.name},{self.size.name})'
  def __str__(self):
    return self.name

# %%
