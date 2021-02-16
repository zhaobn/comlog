
# %%
import numpy as np

# %%
# Global setting
COLORS = [ 'red', 'blue', 'yellow' ]
SHAPES = [ 'circle', 'triangle', 'square' ]
PATTERNS = [ 'stripy', 'dotted', 'plain' ]
SCALES = [ 1, 2, 3, 4 ]

# %%
class Stone:
  ctype = 'stone'
  def __init__(self, color = None, c_scale = None, shape = None, s_scale = None, pattern = None, p_scale = None):
    self.color = color
    self.c_scale = c_scale
    self.shape = shape
    self.s_scale = s_scale
    self.pattern = pattern
    self.p_scale = p_scale
  def __str__(self):
    return f'{self.color}{self.c_scale}_{self.shape}{self.s_scale}_{self.pattern}{self.p_scale}'

# %%
# generate learning data
learning_data = [
  (Stone('red', 2, 'circle', 2, 'plain', 1), Stone('blue', 2, 'circle', 2, 'plain', 3), Stone('red', 2, 'circle', 2, 'plain', 3)),
  (Stone('yellow', 2, 'circle', 2, 'plain', 1), Stone('red', 1, 'square', 2, 'dotted', 1), Stone('yellow', 1, 'square', 2, 'dotted', 1)),
  (Stone('red', 4, 'circle', 2, 'plain', 1), Stone('blue', 4, 'circle', 1, 'plain', 4), Stone('red', 4, 'circle', 1, 'plain', 4)),
  (Stone('blue', 1, 'triangle', 2, 'dotted', 4), Stone('red', 4, 'circle', 3, 'plain', 4), Stone('blue', 4, 'circle', 3, 'plain', 4))
]

# %%
# function generator


# function consumer

# function checker
