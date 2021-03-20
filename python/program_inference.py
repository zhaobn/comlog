
# %%
import pandas as pd
pd.set_option('mode.chained_assignment', None)

from base_terms import *
from helpers import secure_list, names_to_string, print_name
from program_generation import Program_lib_light, Program_lib, data

# %% Basic setup
pms = pd.read_csv('data/rc_cp.csv', index_col=0)
pl = Program_lib(pd.read_csv('data/pm_init.csv', index_col=0, na_filter=False))

# t = [['obj', 'obj'], 'obj']
# pl.generate_program(t)

# %%
def get_base_primitives(terms):
  df = Program_lib_light(pd.DataFrame({'terms': [], 'arg_types': [], 'return_type': [], 'type': [], 'count': []}))
  if isinstance(terms, str):
    terms = eval(terms)
  tm_list = list(pd.core.common.flatten(terms))
  for t in tm_list:
    if isinstance(t, bool) == 0 and t.ctype in ('primitive', 'col', 'shp', 'pat', 'int'):
      df.add(t)
  return df.content
# get_base_primitives('[BC,[B,setColor,I],getColor]')

def find_ret_type(terms):
  terms = list(pd.core.common.flatten(terms))
  first_primitive = next(t for t in terms if isinstance(t,bool)==0 and t.ctype=='primitive')
  return first_primitive.return_type

def get_sub_programs(terms):
  sub_programs = []
  if isinstance(terms, str):
    terms = eval(terms)
  if len(terms) < 2:
    return sub_programs
  else:
    left_index = 1 if len(terms) == 3 else 2
    right_index = 2 if len(terms) == 3 else 1
    if len(secure_list(terms[right_index])) > 1:
      program_dict = {
        'terms': names_to_string(print_name(terms[right_index])),
        'arg_types': '_'.join(['obj'] * terms[0].n_arg),
        'return_type': find_ret_type(terms[right_index]),
        'type': 'program',
        'count': 1,
      }
      sub_programs.append(program_dict)
    sub_programs += get_sub_programs(secure_list(terms[left_index]))
    sub_programs += get_sub_programs(secure_list(terms[right_index]))
    return sub_programs

tm = '[SK, [B, setDensity, [C, [B, setSize, I], S3]], getSize]'
# x = get_sub_programs(tm)

def extract_programs(terms):
  df_bp = get_base_primitives(terms)
  df_pm = pd.DataFrame(get_sub_programs(terms))
  df_pm = df_pm.groupby(by=['terms','arg_types','return_type','type'], as_index=False).agg({'count': pd.Series.count})
  df = df_bp.append(df_pm)
  return df

extract_programs(tm)
