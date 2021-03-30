
# %%
from math import exp
import pandas as pd
from pandas.core import frame
pd.set_option('mode.chained_assignment', None)

from base_terms import *
from helpers import secure_list, names_to_string, print_name, normalize, softmax
from program_generation import Program_lib_light, Program_lib

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
    'terms': [ strip_terms_spaces(terms_str) ],
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

def extract(df, top_n=1, sample=True, base=0):
  ret_df = pd.DataFrame({'terms':[],'arg_types':[],'return_type':[],'type':[],'count':[]})
  if sample == 1:
    df['prob'] = df.apply(lambda row: exp(row['log_prob']), axis=1)
    df['prob'] = normalize(df['prob']) if base == 0 else softmax(df['prob'], base)
    to_add = df.sample(n=top_n, weights='prob')
  else:
    to_add = df.sort_values(['log_prob'], ascending=False).head(top_n)
  for i in range(len(to_add)):
    terms = to_add.iloc[i].terms
    extracted = extract_programs(terms)
    ret_df = pd.concat([ret_df, extracted]).groupby(['terms', 'arg_types', 'return_type','type'], as_index=False)['count'].sum()
  return ret_df

def strip_terms_spaces(terms_str):
  return ','.join([tm.strip() for tm in terms_str.split(',')])

# %%
data_list = [
  {
    'agent': Stone(Red,S1,Triangle,S1,Dotted,S1),
    'recipient': Stone(Yellow,S1,Square,S2,Dotted,S2),
    'result': Stone(Red,S1,Square,S1,Dotted,S2)
  },
  {
    'agent': Stone(Yellow,S2,Square,S2,Dotted,S1),
    'recipient': Stone(Red,S1,Triangle,S1,Plain,S2),
    'result': Stone(Yellow,S1,Triangle,S2,Plain,S2)
  },
  {
    'agent': Stone(Yellow,S2,Triangle,S1,Plain,S1),
    'recipient': Stone(Yellow,S2,Square,S1,Dotted,S1),
    'result': Stone(Yellow,S2,Square,S2,Dotted,S1)
  },
  {
    'agent': Stone(Yellow,S2,Triangle,S1,Plain,S1),
    'recipient': Stone(Red,S1,Triangle,S1,Plain,S1),
    'result': Stone(Yellow,S1,Triangle,S2,Plain,S1)
  },
]
t = [['obj', 'obj'], 'obj']

# %%
pm_init = pd.read_csv('data/pm_init_cut.csv', index_col=0, na_filter=False)

extracted = [None] * len(data_list)
filtered = [None] * len(data_list)
frames = [None] * len(data_list)

for i in range(len(data_list)):
  print(f'-------- {i}-th data --------')
  pl = Program_lib(pm_init)
  enum_programs = pl.bfs(t,1)
  frames[i] = enum_programs
  print(f'Enumed: {len(enum_programs)} frames')
  filtered_programs = pl.filter_program(enum_programs, data_list[i])
  filtered[i] = filtered_programs
  print(f'Filtered: {len(filtered_programs)} programs')
  extracted[i] = extract(filtered_programs)
  print(extracted[i])
  pm_init = pd.concat([ pm_init, extracted[i] ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()

# %%
pm_init = pd.read_csv('data/pm_init.csv', index_col=0, na_filter=False)

extracted = [None] * len(data_list)
filtered = [None] * len(data_list)
frames = [None] * len(data_list)

for i in range(len(data_list)):
  print(f'-------- {i}-th: {len(data_list[:i+1])} data --------')
  pl = Program_lib(pm_init)
  enum_programs = pl.bfs(t,1)
  frames[i] = enum_programs
  print(f'Enumed: {len(enum_programs)} frames')
  filtered_programs = pl.filter_program(enum_programs, data_list[:i+1])
  filtered[i] = filtered_programs
  print(f'Filtered: {len(filtered_programs)} programs')
  extracted[i] = extract(filtered_programs, 2)
  print(extracted[i])
  pm_init = pd.concat([ pm_init, extracted[i] ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()

# %%
learned_lib = pd.read_csv('all.csv', index_col=0, na_filter=False)
pm_init = pd.read_csv('data/pm_init.csv', index_col=0, na_filter=False)
learned_lib = pd.concat([ pm_init, learned_lib ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()

# # strip_terms_spaces(learned_lib.terms.values[19])

# learned_lib['terms'] = learned_lib.apply(lambda row: strip_terms_spaces(row['terms']), axis=1)
# learned_lib = learned_lib.groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()

pl = Program_lib(learned_lib)

new_data = {
  'agent': Stone(Yellow,S3,Circle,S2,Plain,S1),
  'recipient': Stone(Blue,S4,Triangle,S3,Stripy,S1),
  'result': Stone(Blue,S4,Triangle,S3,Dotted,S3)
}
t = [['obj', 'obj'], 'obj']

enum_programs = pl.bfs(t,1)
print(f'Enumed: {len(enum_programs)} frames')
filtered_programs = pl.filter_program(enum_programs, [new_data])
print(f'Filtered: {len(filtered_programs)} programs')
extracted = extract(filtered_programs, 2)
extracted['terms'] = extracted.apply(lambda row: strip_terms_spaces(row['terms']), axis=1)
print(extracted)
pm_init = pd.concat([ learned_lib, extracted ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()

# %%
n2 = pd.read_csv('data/loop_n2.csv', index_col=0, na_filter=False)
inc = pd.read_csv('data/loop_all.csv', index_col=0, na_filter=False)
# %%
