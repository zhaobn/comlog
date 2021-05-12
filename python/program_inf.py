
# %%
import math
import random
import pandas as pd
pd.set_option('mode.chained_assignment', None)
from task_configs import *
from helpers import secure_list, names_to_string, print_name, normalize, softmax
from program_lib import Program_lib_light, Program_lib

# %%
class Gibbs_sampler:
  def __init__(self, program_lib, data_list, frames, iteration, burnin=0, down_weight=1, iter_start=0, data_start=0):
    self.cur_programs = program_lib.content
    self.dir_alpha = program_lib.DIR_ALPHA
    self.data = data_list
    self.frames = frames
    self.dw = down_weight
    self.iter = iteration
    self.burnin = burnin
    self.iter_start = iter_start
    self.data_start = data_start
    self.extraction_history = [[None] * len(data_list)] * iteration if self.inc == 1 else [[None] * iteration]
    # self.filtering_history = [[0] * len(data_list)] * iteration if self.inc == 1 else [[0] * iteration]

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
      if isinstance(t, int):
        df.add(t)
      elif isinstance(t, bool) == 0 and t.ctype in (list(bases) + ['primitive']):
        df.add(t)
    return df.content

  def refactor_router_K(self, pm_dict):
    terms_list = eval(pm_dict['terms'])
    if isinstance(terms_list, list):
      router_str =  terms_list[0].name
      n_dropped = router_str.count('K')
      if n_dropped > 0 and n_dropped < len(router_str):
        new_router = eval(terms_list[0].name.replace('K', ''))
        new_terms = names_to_string(print_name([new_router]+terms_list[1:]))
        return {
            'terms': self.strip_terms_spaces(new_terms),
            'arg_types': '_'.join(['obj']*new_router.n_arg),
            'return_type': pm_dict['return_type'],
            'type': 'program',
            'count': 1,
        }
      else:
        return None
    else:
      return None

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
          'arg_types': '_'.join(['obj'] * terms[right_index][0].n_arg),
          'return_type': self.find_ret_type(terms[right_index]),
          'type': 'program',
          'count': 1,
        }
        sub_programs.append(program_dict)
      sub_programs += self.get_sub_programs(secure_list(terms[left_index]))
      sub_programs += self.get_sub_programs(secure_list(terms[right_index]))
      return sub_programs

  @staticmethod
  def is_all_K(terms):
    terms_eval = eval(terms) if isinstance(terms, str) else terms
    terms_str = print_name(terms_eval)
    first_router = terms_str[0]
    return first_router == 'K'*len(first_router)

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
    if self.is_all_K(terms_str):
      return df
    else:
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
      programs = extracted.query('type=="program"')
      if len(programs) > 0:
        for j in range(len(programs)):
          refactored = self.refactor_router_K(programs.iloc[j].to_dict())
          if refactored is not None:
            ret_df = pd.concat([ret_df, pd.DataFrame([refactored])])
    return ret_df.groupby(['terms', 'arg_types', 'return_type', 'type'], as_index=False)['count'].sum()

  def run(self, type_sig=[['obj','obj'],'obj'], top_n=1, sample=True, base=0, logging=True, save_prefix=''):
    for i in range(self.iter_start, self.iter):
      iter_log = f'Iter {i+1}/{self.iter}({round(100*(i+1)/self.iter, 2)}%)'
      data_start = 0 if i > self.iter_start else self.data_start
      for j in range(data_start, len(self.data)):
        data_log = f'Data {j+1}/{len(self.data)}'
        data = self.data[:(j+1)] if i < 1 else self.data
        # Remove previously-extracted counts
        if i > 1:
          previous = self.extraction_history[i-1][j]
          if previous is not None:
            pms = pd.merge(self.cur_programs, previous, on=['terms', 'arg_types', 'return_type', 'type'], how='outer')
            pms = pms.fillna(0)
            pms['count'] = pms['count_x']-self.dw*pms['count_y'] # dw could range between 0 to 1
            pms = pms[pms['count']>=1][['terms', 'arg_types', 'return_type', 'type', 'count']]
        else:
          pms = self.cur_programs
        pl = Program_lib(pms, self.dir_alpha)
        filtered = pl.filter_program(enumed, data)
        if len(filtered) < 1:
          print('No programs found, filtering again with single input...') if logging else None
          self.filtering_history[i][j] = 0
          filtered = pl.filter_program(enumed, self.data[j])
        else:
          self.filtering_history[i][j] = 1
        extracted = self.extract(filtered, top_n, sample, base)
        print(extracted) if logging else None
        self.extraction_history[i][j] = extracted
        self.cur_programs = pd.concat([ self.cur_programs, extracted ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()
        if len(save_prefix) > 0:
          padding = len(str(self.iter))
          filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')
          pd.DataFrame.from_records(self.filtering_history).to_csv(f'{save_prefix}filter_hist.csv')
          self.cur_programs.to_csv(f'{save_prefix}_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv'


# # %%
# data_list = [
#   {
#     'agent': Stone(Red,S1,Triangle,S1), #,Dotted,S1),
#     'recipient': Stone(Yellow,S1,Square,S2), #,Dotted,S2),
#     'result': Stone(Red,S1,Square,S1), #,Dotted,S2)
#   },
#   {
#     'agent': Stone(Yellow,S2,Square,S2), #,Dotted,S1),
#     'recipient': Stone(Red,S1,Triangle,S1), #,Plain,S2),
#     'result': Stone(Yellow,S1,Triangle,S2), #,Plain,S2)
#   },
#   {
#     'agent': Stone(Yellow,S2,Triangle,S1), #,Plain,S1),
#     'recipient': Stone(Yellow,S2,Square,S1), #,Dotted,S1),
#     'result': Stone(Yellow,S2,Square,S2), #,Dotted,S1)
#   },
#   {
#     'agent': Stone(Yellow,S2,Triangle,S1), #,Plain,S1),
#     'recipient': Stone(Red,S1,Triangle,S1), #,Plain,S1),
#     'result': Stone(Yellow,S1,Triangle,S2), #,Plain,S1)
#   },
# ]

# pm_init = pd.read_csv('data/pm_init_test.csv', index_col=0, na_filter=False)
# g = Gibbs_sampler(Program_lib(pm_init), data_list, iteration=1, burnin=0, inc=1)
# g.run(save_prefix='test', sample=False, top_n=2)

# filtered = pd.read_csv('tests/composition/phase_1/pm_filtered_1_2.csv', index_col=0, na_filter=False)
# extracted = g.extract(filtered, 6, False)
# print(extracted)
