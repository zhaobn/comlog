
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
    # handle both dict or object input
    if isinstance(et, dict):
      terms = et['terms']
      arg_types = et['arg_types']
      return_type = et['return_type']
      name = et['name'] if 'name' in et else ''
    else: # object
      et_terms = print_name(et.terms) if hasattr(et, 'terms') else et.name
      terms = names_to_string(secure_list(et_terms))
      arg_types = args_to_string(et.arg_type)
      return_type = et.return_type
      name = et.name if hasattr(et, 'name') else ''
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
programs_to_add = [ getColor, setColor, eqColor, eqObject, ifElse, ifElse ]
df_pm = add_to_program_lib(df_pm, programs_to_add)
# df_pm = add_to_program_lib(df_pm, {'terms':'[I]', 'arg_types': 'obj', 'return_type': 'obj', 'name': 'I'})
# df_pm.to_csv('program_lib.csv')
# df_pm = pd.read_csv('program_lib.csv')

# %%
def get_cached_program(type_signature, p_source = df_pm):
  arg_t, ret_t = type_signature
  matched_pms = p_source.query(f'arg_types == "{args_to_string(arg_t)}" & return_type == "{ret_t}"')
  return matched_pms if not matched_pms.empty else None

def sample_program(p_source):
  sampled = p_source.sample(n=1, weights = 'count', random_state = 1)
  s_terms, s_arg_t, s_ret_t, = sampled.values[0][:3]
  return {'terms': s_terms, 'arg_types': s_arg_t, 'return_type': s_ret_t}

# sample_program(get_cached_program([['obj'], 'col']))

def get_matched_program(return_type, p_source = df_pm):
  matched_pms = p_source.query(f'return_type == "{return_type}"')
  return matched_pms if not matched_pms.empty else None

# get_matched_program('col')

# %%
def generate_program(type_signature, p_lib = df_pm, depth = 5):
  # check cache status
  cached_pms = get_cached_program(type_signature, p_lib)
  if not cached_pms.empty:
    # return a sample
    sampled_pm = sample_program(cached_pms)
    return sampled_pm
  else:
    # generate new program
    return 2
