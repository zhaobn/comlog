
# %%
import pandas as pd
import numpy as np

from base_terms import *
from list_helpers import args_to_string, names_to_string, print_name

# %%
def init_program_lib():
  return pd.DataFrame({
    'terms': pd.Series([], dtype='str'),
    'arg_types': pd.Series([], dtype='str'),
    'return_type': pd.Series([], dtype='str'),
    'count': pd.Series([], dtype='int'),
    'name': pd.Series([], dtype='str')
  })

# entry contains: ctype, [terms,] arg_type, return_type, name
def add_to_program_lib(p_lib, entry_list):
  entry_list = secure_list(entry_list)
  for et in entry_list:
    if isinstance(et, dict):
      # sampled from program lib
      terms = et['terms']
      arg_types = et['arg_types']
      return_type = et['return_type']
      name = et['name'] if 'name' in et else ''
    elif et.ctype in [ 'col', 'shp', 'pat', 'int', 'obj' ]:
      # base types
      terms = et.name
      arg_types = ''
      return_type = et.ctype
      name = et.name
    elif et.ctype == 'primitive':
      terms = et.name
      arg_types = args_to_string(et.arg_type)
      return_type = et.return_type
      name = et.name
    elif et.ctype == 'program':
      terms = names_to_string(secure_list(print_name(et.terms)))
      arg_types = args_to_string(et.arg_type)
      return_type = et.return_type
      name = ''
    else:
      print('Entry type not found!')
      return(p_lib)
    # check existence
    program_found = p_lib.query(f'terms == "{terms}" & arg_types == "{arg_types}" & return_type == "{return_type}"')
    if program_found.empty:
      # entry is new to lib, add to lib
      df_et = pd.DataFrame({
        'terms': pd.Series([terms], dtype='str'),
        'arg_types': pd.Series([arg_types], dtype='str'),
        'return_type': pd.Series([return_type], dtype='str'),
        'count': pd.Series([1], dtype='int'),
        'name': pd.Series([name], dtype='str')
      })
      p_lib = p_lib.append(df_et, ignore_index=True)
    else:
      # increase counter
      assert len(program_found.index) == 1, 'Duplicated entries in program lib!'
      idx = program_found.index[0]
      p_lib.at[idx, 'count'] += 1

  return p_lib

# %%
df_pm = init_program_lib()
df_pm = add_to_program_lib(df_pm, [
  getColor,
  setColor,
  eqColor,
  eqObject,
  ifElse,
 ])

# df_pm = add_to_program_lib(df_pm, {'terms':'[I]', 'arg_types': 'obj', 'return_type': 'obj', 'name': 'I'})
# df_pm.to_csv('program_lib.csv')
# df_pm = pd.read_csv('program_lib.csv')

# %%
def get_cached_program(type_signature, p_source = df_pm):
  arg_t, ret_t = type_signature
  matched_pms = p_source.query(f'arg_types == "{args_to_string(arg_t)}" & return_type == "{ret_t}"')
  return matched_pms if not matched_pms.empty else None

def sample_program(p_source):
  if p_source is None:
    print('No cache found!')
    return {'terms': 'Error', 'arg_types': '', 'return_type': '', 'name': ''}
  elif len(p_source.index) == 1:
    s_idx = 0
  else:
    counts = p_source['count'].to_list()
    weights = [x / sum(counts) for x in counts]
    s_idx = np.random.choice(np.arange(len(weights)), p = weights)
  s_terms, s_arg_t, s_ret_t, = p_source.values[s_idx][:3]
  return {'terms': s_terms, 'arg_types': s_arg_t, 'return_type': s_ret_t}

def get_matched_program(return_type, p_source = df_pm):
  matched_pms = p_source.query(f'return_type == "{return_type}"')
  return matched_pms if not matched_pms.empty else None

# %%
def sample_router(arg_list, left_args, router = ''):
  if len(arg_list) < 1:
    return router
  else:
    arg = arg_list[0]
    if arg in left_args:
      router += np.random.choice(['C','S'])
      left_args = left_args[:-1] if len(left_args) > 1 else []
    else:
      router += 'B'
    arg_list = arg_list[1:]
    return sample_router(arg_list, left_args, router)

# %%
def generate_program(type_signature, p_lib = df_pm, cur_step = 0, max_step = 5):
  if cur_step > max_step:
    print('Max step exceeded!')
    return None
  elif type_signature == [['obj'], 'obj'] and np.random.random() < 0.5:
    return {'terms': 'I', 'arg_types': 'obj', 'return_type': 'obj'}
  else:
    cur_step += 1
    # check cache status
    cached_pms = get_cached_program(type_signature, p_lib)
    if cached_pms is not None:
      # return a sample
      return sample_program(cached_pms)
    else:
      arg_t, ret_t = type_signature
      if len(arg_t) < 1:
        # return a primitive
        if ret_t == 'col':
          sampled_col = np.random.choice([Red, Blue, Yellow])
          return {'terms': sampled_col.name, 'arg_types': '', 'return_type': 'col', 'name': sampled_col.name}
        elif ret_t == 'bool':
          booleans = [
            {'terms': 'True', 'arg_types': '', 'return_type': 'bool', 'name': 'True'},
            {'terms': 'False', 'arg_types': '', 'return_type': 'bool', 'name': 'False'},
          ]
          return np.random.choice(booleans)
        elif ret_t == 'obj':
          return {'terms': 'randomStone', 'arg_types': '', 'return_type': 'obj', 'name': 'randomStone'}
        else:
          print('Type not found!')
          return {'terms': 'Error', 'arg_types': '', 'return_type': '', 'name': ''}
      else:
        # generate new program
        left = sample_program(get_matched_program(ret_t, p_lib))
        left_args = left['arg_types'].split('_')
        free_index = len(left_args) - 2
        router = sample_router(arg_t, left_args[:(free_index+1)])
        routed_args = eval(router).run({'left': [], 'right': []}, arg_t)
        # expand left side until no un-filled arguments
        left_pm = expand_program(left, routed_args['left'], free_index, p_lib, cur_step, max_step)
        right_pm = generate_program([routed_args['right'], left_args[-1]], p_lib, cur_step, max_step)
        terms = [router, left_pm['terms'], right_pm['terms']]
        return {
          'terms': names_to_string(terms),
          'arg_types': args_to_string(type_signature[0]),
          'return_type': type_signature[1]
        }

def expand_program(candidate, arg_list, free_index, p_lib, cur_step, max_step):
  if free_index < 0:
    return candidate
  else:
    left_args = candidate['arg_types'].split('_')
    if len(arg_list) < 1:
      left_pm = expand_program(candidate, arg_list, free_index - 1, p_lib, cur_step, max_step)
      right_pm = generate_program([arg_list, left_args[free_index]], p_lib, cur_step, max_step)
      terms = [left_pm['terms'], right_pm['terms']]
    else:
      router = sample_router(arg_list, left_args[:free_index])
      routed_args = eval(router).run({'left': [], 'right': []}, arg_list)
      left_pm = expand_program(candidate, routed_args['left'], free_index - 1, p_lib, cur_step, max_step)
      right_pm = generate_program([routed_args['right'], left_args[free_index]], p_lib, cur_step, max_step)
      terms = [router, left_pm['terms'], right_pm['terms']]
    return {
      'terms': names_to_string(terms),
      'arg_types': candidate['arg_types'],
      'return_type': candidate['return_type']
    }

# %%
generate_program([['obj', 'obj'], 'obj'])

# %%
