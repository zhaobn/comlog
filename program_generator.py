
# %%
import pandas as pd
import numpy as np

from base_terms import *
from list_helpers import args_to_string, names_to_string

# %%
class Program_lib:
  def __init__(self, program_list):
    self.content = pd.DataFrame({
      'terms': pd.Series([], dtype='str'),
      'arg_types': pd.Series([], dtype='str'),
      'return_type': pd.Series([], dtype='str'),
      'count': pd.Series([], dtype='int'),
      'name': pd.Series([], dtype='str')
    })
    self.ERROR_TERM = {'terms': 'ERROR', 'arg_types': '', 'return_type': '', 'name': 'ERROR'}
    if len(program_list) > 0:
      self.add(program_list)

  def add(self, entry_list):
    entry_list = secure_list(entry_list)
    for et in entry_list:
      if isinstance(et, dict):
        # sampled from program lib
        terms = et['terms']
        arg_types = et['arg_types']
        return_type = et['return_type']
        name = et['name'] if 'name' in et else ''
      else:
        terms = et.name
        arg_types = args_to_string(et.arg_type)
        return_type = et.return_type
        name = et.name
      # check existence
      program_found = self.content.query(f'terms == "{terms}" & arg_types == "{arg_types}" & return_type == "{return_type}"')
      if program_found.empty:
        # entry is new to lib, add to lib
        df_et = pd.DataFrame({
          'terms': pd.Series([terms], dtype='str'),
          'arg_types': pd.Series([arg_types], dtype='str'),
          'return_type': pd.Series([return_type], dtype='str'),
          'count': pd.Series([1], dtype='int'),
          'name': pd.Series([name], dtype='str')
        })
        self.content = self.content.append(df_et, ignore_index=True)
      else:
        # increase counter
        assert len(program_found.index) == 1, 'Duplicated entries in program lib!'
        idx = program_found.index[0]
        self.content.at[idx, 'count'] += 1

  def get_cached_program(self, type_signature):
    arg_t, ret_t = type_signature
    matched_pms = self.content.query(f'arg_types == "{args_to_string(arg_t)}" & return_type == "{ret_t}"')
    return matched_pms if not matched_pms.empty else None

  def get_matched_program(self, return_type):
    matched_pms = self.content.query(f'return_type == "{return_type}"')
    return matched_pms if not matched_pms.empty else None

  def sample_program(self, p_source):
    if p_source is None:
      print('No cache found!')
      return self.ERROR_TERM
    elif len(p_source.index) == 1:
      s_idx = 0
    else:
      counts = p_source['count'].to_list()
      weights = [x / sum(counts) for x in counts]
      s_idx = np.random.choice(np.arange(len(weights)), p = weights)
    s_terms, s_arg_t, s_ret_t, = p_source.values[s_idx][:3]
    return {'terms': s_terms, 'arg_types': s_arg_t, 'return_type': s_ret_t}

  def sample_cached_program(self, type_signature):
    cached = self.get_cached_program(type_signature)
    if cached is None:
      print('No cache found!')
      return self.ERROR_TERM
    else:
      return self.sample_program(cached)

  def sample_matched_program(self, return_type):
    matched = self.get_matched_program(return_type)
    if matched is None:
      print('No match found!')
      return self.ERROR_TERM
    else:
      return self.sample_program(matched)

  # This is hacky. TODO: do it properly.
  def sample_primitive(self, type):
    if type == 'col':
      sampled_col = np.random.choice([Red, Blue, Yellow])
      return {'terms': sampled_col.name, 'arg_types': '', 'return_type': 'col', 'name': sampled_col.name}
    elif type == 'bool':
      booleans = [
        {'terms': 'True', 'arg_types': '', 'return_type': 'bool', 'name': 'True'},
        {'terms': 'False', 'arg_types': '', 'return_type': 'bool', 'name': 'False'},
      ]
      return np.random.choice(booleans)
    elif type == 'obj':
      return {'terms': 'randomStone', 'arg_types': '', 'return_type': 'obj', 'name': 'randomStone'}
    else:
      print('Type not found!')
      return self.ERROR_TERM

  @staticmethod
  def sample_router(arg_list, free_index):
    assert len(arg_list) > 0, 'No arguments for router!'
    if free_index < 0:
      return 'B' * len(arg_list)
    else:
      return ''.join([np.random.choice(['C', 'B', 'S']) for _ in arg_list])

  # Tail-recursion; righthand-side tree
  def generate_program(self, type_signature, cur_step = 0, max_step = 5, rate = 0.5):
    if cur_step > max_step:
      print('Max step exceeded!')
      return self.ERROR_TERM
    else:
      # Use cached program?
      cached = self.get_cached_program(type_signature)
      if cached is not None and np.random.random() < rate:
        return self.sample_program(cached)
      else:
        cur_step += 1
        arg_t, ret_t = type_signature
        if len(arg_t) < 1:
          # return a primitive
          return self.sample_primitive(ret_t)
        else:
          # generate new program
          left = self.sample_matched_program(ret_t)
          left_args = left['arg_types'].split('_')
          free_index = len(left_args) - 2
          router = self.sample_router(arg_t, free_index)
          routed_args = eval(router).run({'left': [], 'right': []}, arg_t)
          # expand left side until no un-filled arguments
          left_pm = self.expand_program(left, routed_args['left'], free_index, cur_step, max_step)
          right_pm = self.generate_program([routed_args['right'], left_args[-1]], cur_step, max_step)
          terms = [router, left_pm['terms'], right_pm['terms']]
          return {
            'terms': names_to_string(terms),
            'arg_types': args_to_string(type_signature[0]),
            'return_type': type_signature[1]
          }
  # Lefthand-side tree
  def expand_program(self, candidate, arg_list, free_index, cur_step, max_step):
    if free_index < 0:
      return candidate
    else:
      left_args = candidate['arg_types'].split('_')
      if len(arg_list) < 1:
        left_pm = self.expand_program(candidate, arg_list, free_index - 1, cur_step, max_step)
        right_pm = self.generate_program([arg_list, left_args[free_index]], cur_step, max_step)
        terms = [left_pm['terms'], right_pm['terms']]
      else:
        router = self.sample_router(arg_list, free_index-1)
        routed_args = eval(router).run({'left': [], 'right': []}, arg_list)
        left_pm = self.expand_program(candidate, routed_args['left'], free_index-1, cur_step, max_step)
        right_pm = self.generate_program([routed_args['right'], left_args[free_index]], cur_step, max_step)
        terms = [router, left_pm['terms'], right_pm['terms']]
      return {
        'terms': names_to_string(terms),
        'arg_types': candidate['arg_types'],
        'return_type': candidate['return_type']
      }

# %%
pl = Program_lib([
  getColor,
  setColor,
  eqColor,
  eqObject,
  ifElse,
  {'terms': 'I', 'arg_types': 'obj', 'return_type': 'obj', 'name': 'I'}
 ])

# %%
pl.generate_program([['obj'], 'obj'])
