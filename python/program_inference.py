
# %%
import pandas as pd
pd.set_option('mode.chained_assignment', None)

from base_terms import *
from helpers import secure_list, names_to_string, print_name
from program_generation import Program_lib_light, Program_lib

# %% Basic setup
pms = pd.read_csv('data/rc.csv', index_col=0)
pm_init = pd.read_csv('data/pm_init.csv', index_col=0, na_filter=False)
pl = Program_lib(pm_init)

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
    left_index = 1 if len(terms) == 3 else 0
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
# tm = '[SK,[B,setDensity,[C,[B,setSize,I],S3]],getSize]'
# x = get_sub_programs(tm)

def extract_programs(terms):
  terms_eval = eval(terms) if isinstance(terms, str) else terms
  terms_str = terms if isinstance(terms, str) else print_name(terms)
  df = pd.DataFrame({
    'terms': [ terms_str ],
    'arg_types': [ '_'.join(['obj'] * terms_eval[0].n_arg) ],
    'return_type': [ find_ret_type(terms_eval) ],
    'type': [ 'program' ],
    'count': [ 1 ],
  })
  df = df.append(get_base_primitives(terms_eval))
  df_pm = pd.DataFrame(get_sub_programs(terms_eval))
  if len(df_pm) > 0:
    df_pm = df_pm.groupby(by=['terms','arg_types','return_type','type'], as_index=False).agg({'count': pd.Series.count})
    df = df.append(df_pm)
  return df
# extract_programs(tm)

def extract(df, top_n=1):
  ret_df = pd.DataFrame({'terms':[],'arg_types':[],'return_type':[],'type':[],'count':[]})
  to_add = df.sort_values(['log_prob'], ascending=False).head(top_n)
  for i in range(len(to_add)):
    terms = to_add.iloc[i].terms
    extracted = extract_programs(terms)
    ret_df = pd.concat([ret_df, extracted]).groupby(['terms', 'arg_types', 'return_type','type'], as_index=False)['count'].sum()
  return ret_df

# %%
data_list = [
  {
    'agent': Stone(Red,S3,Triangle,S4,Dotted,S1),
    'recipient': Stone(Blue,S1,Square,S3,Dotted,S1),
    'result': Stone(Red,S1,Square,S3,Dotted,S1)
  },
  {
    'agent': Stone(Yellow,S4,Circle,S4,Dotted,S1),
    'recipient': Stone(Yellow,S1,Circle,S3,Plain,S4),
    'result': Stone(Yellow,S1,Circle,S4,Plain,S4)
  },
  {
    'agent': Stone(Yellow,S4,Circle,S3,Plain,S1),
    'recipient': Stone(Blue,S4,Triangle,S1,Dotted,S3),
    'result': Stone(Yellow,S4,Triangle,S4,Dotted,S3)
  },
  {
    'agent': Stone(Blue,S1,Triangle,S3,Plain,S3),
    'recipient': Stone(Red,S3,Circle,S1,Plain,S3),
    'result': Stone(Blue,S3,Square,S1,Dotted,S1)
  },
]

# %%
t = [['obj', 'obj'], 'obj']
extracted = []

# For the first data point
enum_programs = pl.bfs(t,1)
filtered_programs = pl.filter_program(enum_programs, data_list[0]) # 77
extracted.append(extract(filtered_programs, 1))

pm_updated = pd.concat([ pm_init, extracted[0] ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()
plt = Program_lib(pm_updated)
enum_programs_2 = plt.bfs(t,1) # 239
filtered_programs_2 = plt.filter_program(enum_programs_2, data_list[1]) # 77






# %%
iter = 10000
for i in range(iter):
  for d in data_list:
    pl = Program_lib(pm_init)
    enum_programs = pl.bfs(t,1)
    filtered_programs = pl.filter_program(enum_programs, data_list[0]) # 77
    extracted.append(extract(filtered_programs))
    pm_init = pd.concat([ pm_init, extracted[0] ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()
