
# %%
import math
import numpy as np
import pandas as pd
pd.set_option('mode.chained_assignment', None)

from task_terms import *
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
    self.extraction_history = [None] * iteration
    self.filtering_history = [None] * iteration

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
      # df = df.append(self.get_base_primitives(terms_eval))
      # # Add first primitive
      # all_primitives = list(self.cur_programs[self.cur_programs['type']=='primitive'].terms)
      # striped_terms = str(terms)
      # for r in (('Stone',''), ('(',''),(')',''),('[',''),(']','')):
      #   striped_terms = striped_terms.replace(*r)
      # first_primitive = next(x for x in striped_terms.split(',') if x in all_primitives)
      # fp_info = self.cur_programs.query(f'terms=="{first_primitive}"&type=="primitive"').iloc[0].to_dict()
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
      ret_df['count'] = ret_df['count'] * likelihood
      programs = extracted.query('type=="program"')
      if len(programs) > 0:
        for j in range(len(programs)):
          refactored = self.refactor_router_K(programs.iloc[j].to_dict())
          if refactored is not None:
            ret_df = pd.concat([ret_df, pd.DataFrame([refactored])])
    ret_df = ret_df.groupby(['terms', 'arg_types', 'return_type', 'type'], as_index=False)['count'].sum()
    return ret_df

  def merge_lib(self, extracted_df):
    merged_df = pd.merge(self.cur_programs.copy(), extracted_df, how='outer', on=['terms','arg_types','return_type','type']).fillna(0)
    # Increase counter
    merged_df['count'] = merged_df['count_x'] + merged_df['count_y']
    set_df = (merged_df
      .query('count_y==0')[['terms','arg_types','return_type','type','is_init','count','comp_lp','adaptor_lp','log_prob_x']]
      .rename(columns={'log_prob_x': 'log_prob'}))
    # Take care of newly-created programs
    to_set_df = (merged_df
      .query('count_x==0')[['terms','arg_types','return_type','type','count','log_prob_y']]
      .rename(columns={'log_prob_y': 'log_prob'}))
    to_set_df['comp_lp'] = to_set_df['log_prob']
    to_set_df['adaptor_lp'] = 0.0
    to_set_df['is_init'] = 0
    # Merge & take care of probabilities
    temp_lib = Program_lib(pd.concat([set_df, to_set_df], ignore_index=True))
    temp_lib.update_lp_adaptor()
    temp_lib.update_overall_lp()
    return temp_lib.content

  def run(self, frames, top_n=1, sample=True, frame_sample=20, base=0, logging=True, save_prefix='', exceptions_allowed=0):
    frames['prob'] = frames.apply(lambda row: math.exp(row['log_prob']), axis=1)
    for i in range(self.iter_start, self.iter):
      iter_log = f'Iter {i+1}/{self.iter}'
      data = self.data

      # Remove previously-extracted counts
      pms = self.cur_programs.copy()
      if i > 0:
        previous = self.extraction_history[i-1]
        if previous is not None:
          lhs = pms.copy()
          rhs = previous[['terms', 'arg_types', 'return_type', 'type', 'count']]
          pms = pd.merge(lhs, rhs, on=['terms', 'arg_types', 'return_type', 'type'], how='outer').fillna(0)
          pms['count'] = pms['count_x'] - self.dw*pms['count_y'] # dw by default is 1
          pms = pms[pms['count']>=1][['terms', 'arg_types', 'return_type', 'type', 'count', 'log_prob', 'prior']]
          pms['log_prob'] = pl.log_dir(pms['count'], pms['prior'])
      pl = Program_lib(pms, self.dir_alpha)

      # Sample frames
      frames_left = frames.copy()
      filtered = pd.DataFrame({'terms': [], 'log_prob': [], 'n_exceptions': []})
      ns = 0
      while (len(filtered)) < 1 and ns < 100:
        ns += 1
        if len(frames_left) <= frame_sample:
          sampled_frames = frames_left.copy()
        else:
          sampled_frames = frames_left.sample(n=frame_sample, weights='prob').reset_index(drop=True)
        frames_left = frames_left[~frames_left['terms'].isin(sampled_frames['terms'])]
        for k in range(len(sampled_frames)):
          all_programs = pl.unfold_programs_with_lp(sampled_frames.iloc[k].at['terms'], sampled_frames.iloc[k].at['log_prob'], data)
          if len(all_programs) > 0:
            for d in range(len(data)):
              all_programs[f'consistent_{d}'] = all_programs.apply(lambda row: pl.check_program(row['terms'], data[d]), axis=1)
            all_programs['total_consistency'] = all_programs[all_programs.columns[pd.Series(all_programs.columns).str.startswith('consistent')]].sum(axis=1)
            all_programs['n_exceptions'] = len(data) - all_programs['total_consistency']
            passed_pm = all_programs.query(f'n_exceptions<={exceptions_allowed}')
            passed_pm['log_prob'] = passed_pm['log_prob'] - 2*passed_pm['n_exceptions'] # likelihood: exp(-2 * n_exceptions)
            print(f"[{iter_log}|{k}/{len(sampled_frames)}, -{ns}th] {sampled_frames.iloc[k].at['terms']}: {len(passed_pm)} passed") if logging else None
            filtered = filtered.append(passed_pm[['terms', 'log_prob', 'n_exceptions']], ignore_index=True)
      # Extract resusable bits
      if len(filtered) < 1:
        print('Nothing consistent, skipping to next...') if logging else None
      else:
        # Sample or add all
        if len(filtered) <= top_n or sample == 0:
          to_add = filtered.copy()
        else:
          filtered['prob'] = filtered.apply(lambda row: math.exp(row['log_prob']), axis=1)
          filtered['prob'] = normalize(filtered['prob']) if base == 0 else softmax(filtered['prob'], base)
          to_add = filtered.sample(n=top_n, weights='prob')
        # Add chunk to lib (see program_inf for recursive version)
        to_add['arg_types'] = 'egg_num'
        to_add['return_type'] = 'num'
        to_add['type'] = 'program'
        to_add['count'] = 1
        if len(to_add) > 1:
          extracted = (to_add
            .groupby(by=['terms','arg_types','return_type','type'], as_index=False)
            .agg({'count': pd.Series.count, 'log_prob': pd.Series.max})
            .reset_index(drop=1))
        else:
          extracted = to_add[['terms','arg_types','return_type','type','count','log_prob']]
        print(extracted) if logging else None
        self.extraction_history[i] = extracted
        self.cur_programs = self.merge_lib(extracted)
        if len(save_prefix) > 0:
          padding = len(str(self.iter))
          filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}.csv')
          extracted.to_csv(f'{save_prefix}_extracted_{str(i+1).zfill(padding)}.csv')
          self.cur_programs.to_csv(f'{save_prefix}_lib_{str(i+1).zfill(padding)}.csv')

# %% Debug
all_data = pd.read_json('for_exp/config.json')
task_ids = {
  'learn_a': [23, 42, 61],
  'learn_b': [35, 50, 65],
  'gen': [82, 8, 20, 4, 98, 48, 71, 40],
}
task_ids['gen'].sort()

task_data = {}
for item in task_ids:
  task_data[item] = []
  for ti in task_ids[item]:
    transformed = {}
    data = all_data[all_data.trial_id==ti]
    _, agent, recipient, result = list(data.iloc[0])
    transformed['agent'] = eval(f'Egg(S{agent[1]},O{agent[4]})')
    transformed['recipient'] = int(recipient[-2])
    transformed['result'] = int(result[-2])
    task_data[item].append(transformed)

all_frames = pd.read_csv('data/task_frames.csv',index_col=0)
data_len_a = len(task_data['learn_a'])
data_len_b = len(task_data['learn_b'])


# %%
pl = Program_lib(pd.read_csv('data/task_pm.csv', index_col=0, na_filter=False))
g1 = Gibbs_sampler(pl, task_data['learn_a'], iteration=2)
# g1.run(all_frames, top_n=1, save_prefix='./sims/samples/test')

frames = all_frames
data = task_data['learn_a']
top_n=1
sample=True
frame_sample=20
base=0
logging=True
save_prefix=''
exceptions_allowed=0
iter_log = ''
pms = g1.cur_programs.copy()
pl = Program_lib(pms, g1.dir_alpha)

# %%
