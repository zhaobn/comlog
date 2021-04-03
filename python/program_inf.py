
# %%
import math
import pandas as pd
pd.set_option('mode.chained_assignment', None)

from base_terms import *
from helpers import secure_list, names_to_string, print_name, normalize, softmax
from program_lib import Program_lib_light, Program_lib

# %%
class Gibbs_sampler:
  def __init__(self, program_lib, data_list, iteration, burnin=0, down_weight=1):
    self.cur_programs = program_lib.content
    self.dir_alpha = program_lib.DIR_ALPHA
    self.data = data_list
    self.dw = down_weight
    self.iter = iteration
    self.burnin = burnin
    self.extraction_history = [[None] * len(data_list)] * iteration

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
    bases = set(list(self.cur_programs[self.cur_programs['type']=='base_term'].return_type))
    if isinstance(terms, str):
      terms = eval(terms)
    tm_list = list(pd.core.common.flatten(terms))
    for t in tm_list:
      if isinstance(t, bool) == 0 and t.ctype in (list(bases) + ['primitive']):
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
      'terms': [ terms_str ],
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
      df['prob'] = df.apply(lambda row: math.exp(row['log_prob']), axis=1)
      df['prob'] = normalize(df['prob']) if base == 0 else softmax(df['prob'], base)
      to_add = df.sample(n=top_n, weights='prob')
    else:
      to_add = df.sort_values(['log_prob'], ascending=False).head(top_n)
    for i in range(len(to_add)):
      terms = to_add.iloc[i].terms
      extracted = self.extract_programs(terms)
      ret_df = pd.concat([ret_df, extracted])
      ret_df['terms'] = ret_df.apply(lambda row: self.strip_terms_spaces(row['terms']), axis=1)
    return ret_df.groupby(['terms', 'arg_types', 'return_type', 'type'], as_index=False)['count'].sum()

  def run(self, type_sig=[['obj', 'obj'], 'obj'], top_n=1, sample=True, base=0, logging=True, save_prefix=''):
    for i in range(self.iter):
      print(f'Running {i+1}/{self.iter} ({round(100*(i+1)/self.iter, 2)}%):') if logging else None
      for j in range(len(self.data)):
        print(f'---- {j+1}-th out of {len(self.data)} ----') if logging else None
        if i < 1:
          # incrementally
          data = self.data[:(j+1)]
          pms = self.cur_programs
        else:
          # Use full batch
          data = self.data
          # Remove previously-extracted counts
          pms = pd.merge(self.cur_programs, self.extraction_history[i-1][j], on=['terms', 'arg_types', 'return_type', 'type'], how='outer')
          pms = pms.fillna(0)
          pms['count'] = pms['count_x'] - self.dw*pms['count_y'] # dw ranges 0 to 1
          pms = pms[pms['count']>=1][['terms', 'arg_types', 'return_type', 'type', 'count']]
        pl = Program_lib(pms, self.dir_alpha)
        enumed = pl.bfs(type_sig, 1)
        filtered = pl.filter_program(enumed, data)
        if len(filtered) < 1:
          print('No programs found, filtering again with single input...') if logging else None
          filtered = pl.filter_program(enumed, self.data[j])
        extracted = self.extract(filtered, top_n, sample, base)
        print(extracted) if logging else None
        self.extraction_history[i][j] = extracted
        self.cur_programs = pd.concat([ self.cur_programs, extracted ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()
        if len(save_prefix) > 0:
          padding = len(str(self.iter))
          self.cur_programs.to_csv(f'{save_prefix}_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')
# # %%
# data_list = [
#   {
#     'agent': Stone(Red,S1,Triangle,S1,Dotted,S1),
#     'recipient': Stone(Yellow,S1,Square,S2,Dotted,S2),
#     'result': Stone(Red,S1,Square,S1,Dotted,S2)
#   },
#   {
#     'agent': Stone(Yellow,S2,Square,S2,Dotted,S1),
#     'recipient': Stone(Red,S1,Triangle,S1,Plain,S2),
#     'result': Stone(Yellow,S1,Triangle,S2,Plain,S2)
#   },
#   {
#     'agent': Stone(Yellow,S2,Triangle,S1,Plain,S1),
#     'recipient': Stone(Yellow,S2,Square,S1,Dotted,S1),
#     'result': Stone(Yellow,S2,Square,S2,Dotted,S1)
#   },
#   {
#     'agent': Stone(Yellow,S2,Triangle,S1,Plain,S1),
#     'recipient': Stone(Red,S1,Triangle,S1,Plain,S1),
#     'result': Stone(Yellow,S1,Triangle,S2,Plain,S1)
#   },
# ]

# pm_init = pd.read_csv('data/pm_init_cut.csv', index_col=0, na_filter=False)
# x = Gibbs_sampler(Program_lib(pm_init), data_list, iteration=5, burnin=0)
# x.run(save_prefix='test_data/test', sample=False, top_n=2)
