
# %%
import math
import random
import numpy as np
import pandas as pd
pd.set_option('mode.chained_assignment', None)

from task_configs import *
from helpers import secure_list, names_to_string, print_name, normalize, softmax
from program_lib import Program_lib_light, Program_lib

# %%
class Gibbs_sampler:
  def __init__(self, program_lib, data_list, iteration, inc=False, burnin=0, down_weight=1, iter_start=0, data_start=0):
    self.init_programs = program_lib.content
    self.cur_programs = program_lib.content
    self.dir_alpha = program_lib.DIR_ALPHA
    self.data = data_list
    self.dw = down_weight
    self.iter = iteration
    self.inc = inc
    self.burnin = burnin
    self.iter_start = iter_start
    self.data_start = data_start
    self.extraction_history = [[None] * len(data_list)] * iteration if self.inc == 1 else [[None] * iteration]
    self.filtering_history = np.zeros((iteration, len(data_list)))

  @staticmethod
  def find_ret_type(terms):
    terms = list(pd.core.common.flatten(terms))
    first_primitive = next(t for t in terms if isinstance(t,bool)==0 and t.ctype=='primitive')
    return first_primitive.return_type

  @staticmethod
  def strip_terms_spaces(terms_str):
    return ','.join([tm.strip() for tm in terms_str.split(',')])

  def get_base_primitives(self, terms):
    df = Program_lib_light(pd.DataFrame(columns=['terms','arg_types','return_type','type','count']))
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
          'terms': self.strip_terms_spaces(names_to_string(print_name(terms[right_index]))),
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
      # # # Add first primitive
      # # all_primitives = list(self.cur_programs[self.cur_programs['type']=='primitive'].terms)
      # # striped_terms = str(terms)
      # # for r in (('Stone',''), ('(',''),(')',''),('[',''),(']','')):
      # #   striped_terms = striped_terms.replace(*r)
      # # first_primitive = next(x for x in striped_terms.split(',') if x in all_primitives)
      # # fp_info = self.cur_programs.query(f'terms=="{first_primitive}"&type=="primitive"').iloc[0].to_dict()
      # df = df.append(pd.DataFrame({
      #   'terms': [ first_primitive ],
      #   'arg_types': [ fp_info['arg_types'] ],
      #   'return_type': [ fp_info['return_type']],
      #   'type': [ 'primitive' ],
      #   'count': [ 1 ],
      # }))
      # Add subtrees
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
      if 'n_exceptions' in to_add.columns:
        likelihood = math.exp(-2 * to_add.iloc[i].n_exceptions)
      else:
        likelihood = 1
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
    ret_df = ret_df.groupby(['terms', 'arg_types', 'return_type', 'type'], as_index=False)['count'].sum()
    ret_df['count'] = ret_df['count'] * likelihood
    return ret_df

  def run(self, type_sig=[['obj', 'obj'], 'obj'], top_n=1, sample=True, base=0, logging=True, save_prefix=''):
    for i in range(self.iter_start, self.iter):
      print(f'Running {i+1}/{self.iter} ({round(100*(i+1)/self.iter, 2)}%):') if logging else None
      data_start = 0 if i > self.iter_start else self.data_start
      if self.inc == 1:
        for j in range(data_start, len(self.data)):
          print(f'---- {j+1}-th out of {len(self.data)} ----') if logging else None
          if i < 1:
            # incrementally
            data = self.data[:(j+1)]
            pms = self.cur_programs
          else:
            # Use full batch
            data = self.data
            # Remove previously-extracted counts
            previous = self.extraction_history[i-1][j]
            if previous is not None:
              pms = pd.merge(self.cur_programs, previous, on=['terms', 'arg_types', 'return_type', 'type'], how='outer')
              pms = pms.fillna(0)
              pms['count'] = pms['count_x'] - self.dw*pms['count_y'] # dw ranges 0 to 1
              pms = pms[pms['count']>=1][['terms', 'arg_types', 'return_type', 'type', 'count']]
            else:
              pms = self.cur_programs
          pl = Program_lib(pms, self.dir_alpha)
          enumed = pl.bfs(type_sig, 1)
          filtered = pl.filter_program(enumed, data)
          if len(filtered) < 1:
            print('No programs found, filtering again with single input...') if logging else None
            self.filtering_history[i][j] = 0
            filtered = pl.filter_program(enumed, self.data[j])
          else:
            self.filtering_history[i][j] = 1
            padding = len(str(self.iter))
            filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')
          extracted = self.extract(filtered, top_n, sample, base)
          print(extracted) if logging else None
          self.extraction_history[i][j] = extracted
          self.cur_programs = pd.concat([ self.cur_programs, extracted ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()
          if len(save_prefix) > 0:
            padding = len(str(self.iter))
            filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')
            pd.DataFrame.from_records(self.filtering_history).to_csv(f'{save_prefix}filter_hist.csv')
            self.cur_programs.to_csv(f'{save_prefix}_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')
      else: # use full batch
        pms = self.cur_programs
        data = self.data
        pl = Program_lib(pms, self.dir_alpha)
        enumed = pl.bfs(type_sig, 1)
        filtered = pl.filter_program(enumed, data)
        if len(filtered) < 1:
          self.filtering_history[0][i] = 0
          print('No programs found, filtering again with random input...') if logging else None
          rd_idx = random.choice(range(len(data)))
          filtered = pl.filter_program(enumed, self.data[rd_idx])
        else:
          self.filtering_history[0][i] = 1
        extracted = self.extract(filtered, top_n, sample, base)
        print(extracted) if logging else None
        self.extraction_history[0][i] = extracted
        self.cur_programs = pd.concat([ self.cur_programs, extracted ]).groupby(['terms','arg_types','return_type','type'], as_index=False)['count'].sum()
        if len(save_prefix) > 0:
          padding = len(str(self.iter))
          filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}.csv')
          pd.DataFrame(self.filtering_history).to_csv(f'{save_prefix}filter_hist.csv')
          self.cur_programs.to_csv(f'{save_prefix}_{str(i+1).zfill(padding)}.csv')


# # %%
# from base_terms import *

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
# g = Gibbs_sampler(Program_lib(pm_init), data_list, iteration=1, burnin=0, inc=1)
# # g.run(save_prefix='test', sample=False, top_n=2)

# filtered = pd.read_csv('data/pm_filtered_1_2.csv', index_col=0, na_filter=False)
# extracted = g.extract(filtered, 1, sample=1)
# print(extracted)

# # %%
# filtered = pd.read_csv('sf.csv', index_col=0, na_filter=False)
# to_add = filtered.sample(n=1, weights='prob')
# terms = to_add.iloc[0].terms

# task_data_df = pd.read_csv('data/task_data.csv')
# task_data = []
# for i in range(len(task_data_df)):
#   tdata = task_data_df.iloc[i].to_dict()
#   task = {
#     'agent': eval(tdata['agent']),
#     'recipient': eval(tdata['recipient']),
#     'result': eval(tdata['result'])
#   }
#   task_data.append(task)

# pm_init = pd.read_csv('data/task_pm.csv',index_col=0,na_filter=False)
# all_frames = pd.read_csv('data/task_frames.csv',index_col=0)
# g = Gibbs_sampler(Program_lib(pm_init), task_data, iteration=1000)

# %%
