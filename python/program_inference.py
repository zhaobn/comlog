
# %%
from math import exp
import pandas as pd
from pandas.core import frame
pd.set_option('mode.chained_assignment', None)

from base_terms import *
from helpers import secure_list, names_to_string, print_name, normalize, softmax
from program_generation import Program_lib_light, Program_lib

# %%
class Gibbs_sampler:
  def __init__(self, programs, dir_alpha, data_list, down_weight, iteration, burnin):
    self.cur_programs = programs
    self.dir_alpha = dir_alpha
    self.data = data_list
    self.dw = down_weight
    self.iter = iteration
    self.burnin = burnin
    self.extraction_history = [[None] * len(data_list)] * iteration

  @property
  def program_lib(self):
    return Program_lib(self.cur_programs, self.dir_alpha)

  @staticmethod
  def find_ret_type(terms):
    terms = list(pd.core.common.flatten(terms))
    first_primitive = next(t for t in terms if isinstance(t,bool)==0 and t.ctype=='primitive')
    return first_primitive.return_type

  @staticmethod
  def strip_terms_spaces(terms_str):
    return ','.join([tm.strip() for tm in terms_str.split(',')])

  def get_base_primitives(self, terms):
    df = Program_lib_light(pd.DataFrame({'terms': [], 'arg_types': [], 'return_type': [], 'type': [], 'count': []}))
    if isinstance(terms, str):
      terms = eval(terms)
    tm_list = list(pd.core.common.flatten(terms))
    for t in tm_list:
      if isinstance(t, bool) == 0 and t.ctype in (list(self.program_lib.SET_MARKERS) + ['primitive']):
        df.add(t)
    return df.content

  def get_sub_programs(self, terms):
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
          'return_type': self.find_ret_type(terms[right_index]),
          'type': 'program',
          'count': 1,
        }
        sub_programs.append(program_dict)
      sub_programs += self.get_sub_programs(secure_list(terms[left_index]))
      sub_programs += self.get_sub_programs(secure_list(terms[right_index]))
      return sub_programs

  def extract_programs(self, terms):
    terms_eval = eval(terms) if isinstance(terms, str) else terms
    terms_str = terms if isinstance(terms, str) else print_name(terms)
    df = pd.DataFrame({
      'terms': [ self.strip_terms_spaces(terms_str) ],
      'arg_types': [ '_'.join(['obj'] * terms_eval[0].n_arg) ],
      'return_type': [ self.find_ret_type(terms_eval) ],
      'type': [ 'program' ],
      'count': [ 1 ],
    })
    df = df.append(self.get_base_primitives(terms_eval))
    df_pm = pd.DataFrame(self.get_sub_programs(terms_eval))
    if len(df_pm) > 0:
      df_pm = df_pm.groupby(by=['terms','arg_types','return_type','type'], as_index=False).agg({'count': pd.Series.count})
      df = df.append(df_pm)
    return df

  def extract(self, df, top_n=1, sample=True, base=0):
    ret_df = pd.DataFrame({'terms':[],'arg_types':[],'return_type':[],'type':[],'count':[]})
    if sample == 1:
      df['prob'] = df.apply(lambda row: exp(row['log_prob']), axis=1)
      df['prob'] = normalize(df['prob']) if base == 0 else softmax(df['prob'], base)
      to_add = df.sample(n=top_n, weights='prob')
    else:
      to_add = df.sort_values(['log_prob'], ascending=False).head(top_n)
    for i in range(len(to_add)):
      terms = to_add.iloc[i].terms
      extracted = self.extract_programs(terms)
      ret_df = pd.concat([ret_df, extracted]).groupby(['terms', 'arg_types', 'return_type','type'], as_index=False)['count'].sum()
    return ret_df

  def run(self, type_sig=[['obj', 'obj'], 'obj']):
    for i in range(self.iter):
      print(f'Running {i+1}/{self.iter} ({round(100*(i+1)/self.iter, 2)}%):')
      for j in range(len(self.data)):
        data = self.data[:(j+1)] if i < 1 else self.data
        pl = Program_lib(self.cur_programs, self.dir_alpha)
        print(f'-------- {j}-th data --------')
        filtered = pl.bfs_filter(type_sig, 1, data)
        extracted = self.extract(filtered, 1)
        print(extracted)
        self.extraction_history[i][j] = extracted
        self.cur_programs = pd.concat([ self.cur_programs, extracted ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()
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

pm_init = pd.read_csv('data/pm_init_cut.csv', index_col=0, na_filter=False)
Gibbs_sampler(pm_init, 0.1, data_list, 0, 1, 0).run()

# %%
