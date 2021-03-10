
# %%
import pandas as pd
from numpy import random as np_random

from base_terms import *
from list_helpers import args_to_string, names_to_string

# %%
class Program_lib:
  def __init__(self, program_list = [],
  base_list = [ True, False, Red, Blue, Yellow,
  Circle, Square, Triangle, Dotted, Plain, S1, S2, S3, S4 ]):
    self.content = pd.DataFrame({
      'terms': pd.Series([], dtype='str'),
      'arg_types': pd.Series([], dtype='str'),
      'return_type': pd.Series([], dtype='str'),
      'count': pd.Series([], dtype='int'),
      'name': pd.Series([], dtype='str')
    })
    self.base_terms = copy(self.content)
    self.ERROR_TERM = {'terms': 'ERROR', 'arg_types': '', 'return_type': '', 'name': 'ERROR'}
    if len(program_list) > 0: self.add(program_list)
    if len(base_list) > 0: self.add_bases(base_list)

  def add(self, entry_list):
    entry_list = secure_list(entry_list)
    for et in entry_list:
      if isinstance(et, dict):
        # sampled from program lib
        terms = et['terms']
        arg_types = et['arg_types']
        return_type = et['return_type']
        name = et['name'] if 'name' in et else ''
      elif et.ctype == 'primitive':
        terms = et.name
        arg_types = args_to_string(et.arg_type)
        return_type = et.return_type
        name = et.name
      else:
        print('Adding to program lib: Bad entry type!')
        pass
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
        assert len(program_found.index) == 1, 'Duplicated entries in program lib!'
        idx = program_found.index[0]
        self.content.at[idx, 'count'] += 1

  def add_bases(self, base_list):
    base_list = secure_list(base_list)
    for bt in base_list:
      if isinstance(bt, dict):
        # sampled from program generation
        terms = bt['terms']
        return_type = bt['return_type']
      elif isinstance(bt, bool):
        terms = 'True' if bt == True else 'False'
        return_type = 'bool'
      else:
        terms = bt.name
        return_type = bt.ctype
      # check existence
      found = self.base_terms.query(f'return_type == "{return_type}" & terms == "{terms}"')
      if found.empty:
        self.base_terms = self.base_terms.append(pd.DataFrame({
          'terms': pd.Series([terms], dtype='str'),
          'arg_types': pd.Series([''], dtype='str'),
          'return_type': pd.Series([return_type], dtype='str'),
          'count': pd.Series([1], dtype='int'),
          'name': pd.Series([terms], dtype='str'),
        }), ignore_index=True)
      elif len(found.index) > 1:
        print('Duplicated base terms!'); exit
      else:
        self.base_terms.at[found.index[0], 'count'] += 1

  def get_cached_program(self, type_signature):
    arg_t, ret_t = type_signature
    matched_pms = self.content.query(f'arg_types == "{args_to_string(arg_t)}" & return_type == "{ret_t}"')
    return matched_pms if not matched_pms.empty else None

  def get_matched_program(self, return_type):
    matched_pms = self.content.query(f'return_type == "{return_type}"')
    return matched_pms if not matched_pms.empty else None

  def sample_program(self, p_source, add=False):
    if p_source is None:
      print('No cache found!')
      return self.ERROR_TERM
    else:
      sampled = p_source.sample(n=1, weights='count').iloc[0].to_dict()
      if add:
        self.add(sampled)
      return sampled

  def sample_cached_program(self, type_signature, add):
    cached = self.get_cached_program(type_signature)
    if cached is None:
      print('No cache found!')
      return self.ERROR_TERM
    else:
      return self.sample_program(cached, add)

  def sample_matched_program(self, return_type, add=False):
    matched = self.get_matched_program(return_type)
    if matched is None:
      print('No match found!')
      return self.ERROR_TERM
    else:
      sampled = self.sample_program(matched, add)
      return sampled

  def sample_base(self, type, add=False):
    if type == 'obj':
      color = self.sample_base('col', add)
      color_scale = self.sample_base('int', add)
      shape = self.sample_base('shp', add)
      shape_scale = self.sample_base('int', add)
      pattern = self.sample_base('pat', add)
      pattern_scale = self.sample_base('int', add)
      sampled_props = [ color, color_scale, shape, shape_scale, pattern, pattern_scale ]
      stone = 'Stone(' + ','.join([p['name'] for p in sampled_props]) + ')'
      return {'terms': stone, 'arg_types': '', 'return_type': 'obj', 'name': stone}
    else:
      bases = self.base_terms.query(f'return_type == "{type}"')
      if bases is None or bases.empty:
        print('No base terms found!')
        return self.ERROR_TERM
      else:
        sampled = bases.sample(n=1, weights='count').iloc[0].to_dict()
        if add:
          self.add_bases(sampled)
        return sampled

  @staticmethod
  def sample_router(arg_list, free_index):
    assert len(arg_list) > 0, 'No arguments for router!'
    if free_index < 0:
      return 'B' * len(arg_list)
    else:
      return ''.join([np_random.choice(['C', 'B', 'S']) for _ in arg_list])

  # Tail-recursion; righthand-side tree
  def generate_program(self, type_signature, cur_step = 0, max_step = 5, cache_rate = 0.5):
    if cur_step > max_step:
      print('Max step exceeded!')
      return self.ERROR_TERM
    else:
      # Use cached program?
      cached = self.get_cached_program(type_signature)
      if cached is not None and np_random.random() < cache_rate:
        sampled = self.sample_program(cached, add=True)
        return sampled
      else:
        cur_step += 1
        arg_t, ret_t = type_signature
        if len(arg_t) < 1:
          # return a base term
          base_term = self.sample_base(ret_t, add=True)
          return base_term
        else:
          # generate new program
          left = self.sample_matched_program(ret_t, add=True)
          left_args = left['arg_types'].split('_')
          free_index = len(left_args) - 2
          router = self.sample_router(arg_t, free_index)
          routed_args = eval(router).run({'left': [], 'right': []}, arg_t)
          # expand left side until no un-filled arguments
          left_pm = self.expand_program(left, routed_args['left'], free_index, cur_step, max_step)
          right_pm = self.generate_program([routed_args['right'], left_args[-1]], cur_step, max_step)
          terms = [router, left_pm['terms'], right_pm['terms']]
          program_dict = {
            'terms': names_to_string(terms),
            'arg_types': args_to_string(type_signature[0]),
            'return_type': type_signature[1]
          }
          # add to program lib
          self.add(program_dict) if 'ERROR' not in program_dict['terms'] else None
          return program_dict

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

pl = Program_lib([
  getColor, setColor, eqColor,
  getSaturation, setSaturation, eqSaturation,
  getShape, setShape, eqShape,
  getSize, setSize, eqSize,
  getPattern, setPattern, eqPattern,
  getDensity, setDensity, eqDensity,
  eqObject,
  ifElse,
  {'terms': 'I', 'arg_types': 'obj', 'return_type': 'obj', 'name': 'I'}
 ])

# %%
pl.generate_program([['obj'], 'obj'], cache_rate = 0.1)


# %% Tests
# s = eval(pl.sample_base('obj')['terms'])
# t = eval(pl.sample_base('obj')['terms'])
# Program([SC, [CS, [BB, ifElse, eqObject], I], I]).run([t,t]).name
# Program([B, [setColor, Stone(Yellow,S1,Triangle,S2,Plain,S4)], getColor]).run(s).name
# Program([B, [setShape, Stone(Red,S2,Circle,S3,Dotted,S4)], [B, getShape, [B, [setPattern, Stone(Blue,S2,Square,S2,Plain,S4)], getPattern]]]).run(s).name
