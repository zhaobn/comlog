# %%
import math
import numpy as np
import pandas as pd

from base_classes import Program
from base_terms import B,C,S,K,BB,BC,BS,BK,CB,CC,CS,CK,SB,SC,SS,SK,KB,KC,KS,KK
from program_lib import Program_lib
from program_inf import Gibbs_sampler
from task_configs import *

# %%
class Task_lib(Program_lib):
  def __init__(self, df, dir_alpha=0.1):
    Program_lib.__init__(self, df, dir_alpha)

  @staticmethod
  def check_program(terms, data):
    result = Program(eval(terms)).run([data['agent'], data['recipient']])
    return result == data['result'].length.value

  def sample_base(self, type, add):
    if type == 'obj':
      stripe = self.sample_base('stripe', add)
      dot = self.sample_base('dot', add)
      length = self.sample_base('length', add)
      sampled_props = [stripe, dot, length]
      stone = 'Stone(' + ','.join([p['terms'] for p in sampled_props]) + ')'
      return {'terms': stone, 'arg_types': '', 'return_type': 'obj', 'type': 'base_term'}
    else:
      bases = self.content.query(f'return_type=="{type}"&type=="base_term"')
      if bases is None or bases.empty:
        print('No base terms found!')
        return self.ERROR_TERM
      else:
        sampled = bases.sample(n=1, weights='count').iloc[0].to_dict()
        if add:
          self.add(sampled)
        return sampled
  def get_all_objs(self):
    stones_df = pd.DataFrame({'terms': []})
    stripe_df = self.content.query('return_type=="stripe"&type=="base_term"')
    dot_df = self.content.query('return_type=="dot"&type=="base_term"')
    length_df = self.content.query('return_type=="length"&type=="base_term"')
    for s in range(len(stripe_df)):
      for o in range(len(dot_df)):
        for l in range(len(length_df)):
          stone_feats = [
            stripe_df.iloc[s].at['terms'],
            dot_df.iloc[o].at['terms'],
            length_df.iloc[l].at['terms'],
          ]
          counts = [
            stripe_df.iloc[s].at['count'],
            dot_df.iloc[o].at['count'],
            length_df.iloc[l].at['count'],
          ]
          stones_df = stones_df.append(pd.DataFrame({'terms': [f'Stone({",".join(stone_feats)})'], 'count': [sum(counts)]}), ignore_index=True)
    stones_df['log_prob'] = self.log_dir(list(stones_df['count']))
    return stones_df[['terms', 'log_prob']]

# # %%
# pm_task = pd.read_csv('data/task_pm.csv', index_col=0, na_filter=False)
# pl = Task_lib(pm_task)
# pl.update_log_prob(init=True)
# pl.update_log_prob(init=False)
# (pl.content.sort_values(by=['type','return_type','arg_types','terms'])
#   .reset_index(drop=True)
#   .to_csv('data/task_pm.csv'))

# pm_init = pd.read_csv('data/task_pm.csv',index_col=0,na_filter=False)
# pl = Task_lib(pm_init)
# t = [['obj', 'obj'], 'num']

# rf = pl.typed_enum(t,1)
# # rf2 = pl.typed_enum(t,2)
# rf.to_csv('data/task_frames.csv')

# %%
class Task_gibbs(Gibbs_sampler):
  def __init__(self, program_lib, data_list, iteration, inc=True, burnin=0, down_weight=1, iter_start=0, data_start=0):
    Gibbs_sampler.__init__(self, program_lib, data_list, iteration, inc, burnin, down_weight, iter_start, data_start)

  def merge_lib(self, extracted_df):
    merged_df = pd.merge(self.cur_programs.copy(), extracted_df, how='outer', on=['terms','arg_types','return_type','type']).fillna(0)
    merged_df['count'] = merged_df['count_x'] + merged_df['count_y']
    set_df = merged_df.query('log_prob!=0|type=="primitive"')[['terms','arg_types','return_type','type','count','log_prob']]
    # Now take care of newly-created programs
    to_set_df = merged_df.query('log_prob==0&type!="primitive"')[['terms','arg_types','return_type','type','count','log_prob']]
    to_set_df = to_set_df.reset_index(drop=True)
    for i in range(len(to_set_df)):
      # Compute prior prob
      log_prob = 0
      terms = to_set_df.iloc[i].terms
      for r in (('Stone',''), ('(',''),(')',''),('[',''),(']','')):
        terms = terms.replace(*r)
      terms_list = terms.split(',')
      for j in range(len(terms_list)):
        tm = terms_list[j]
        found = set_df[set_df['terms']==tm]
        if len(found)==1:
          log_prob += found['log_prob'].values[0]
        elif len(found)>1:
          log_prob += found[found['type']=='program']['log_prob'].values[0]
        else: # routers
          next_tm = eval(terms_list[j+1])
          if not isinstance(next_tm,bool) or not isinstance(next_tm,int):
            if next_tm.ctype=='primitive':
              log_prob += 0
            elif tm == 'I':
              log_prob += math.log(1/(2**len(tm)))
            else:
              log_prob += math.log(1/(4**len(tm)))
          else:
            log_prob += math.log(1/(4**len(tm)))
      to_set_df.at[i,'log_prob']=log_prob
    return pd.concat([set_df, to_set_df],ignore_index=True).reset_index(drop=True)

  def run(self, frames, top_n=1, sample=True, frame_sample=20, base=0, logging=True, save_prefix='', exceptions_allowed=0):
    frames['prob'] = frames.apply(lambda row: math.exp(row['log_prob']), axis=1)
    for i in range(self.iter_start, self.iter):
      iter_log = f'Iter {i+1}/{self.iter}'
      data_start = 0 if i > self.iter_start else self.data_start
      for j in range(data_start, len(self.data)):
        frames_left = frames.copy()
        n_exceptions_allowed = 0 if exceptions_allowed >= j+1 else exceptions_allowed
        data_log = f'Data {j+1}/{len(self.data)}'
        data = self.data[:(j+1)] if i < 1 else self.data
        # Remove previously-extracted counts - start from scratch for each iteration
        pms = self.init_programs
        # if i > 0:
        #   previous = self.extraction_history[i-1][j]
        #   if previous is not None:
        #     lhs = self.cur_programs
        #     rhs = previous[['terms', 'arg_types', 'return_type', 'type', 'count']]
        #     pms = pd.merge(lhs, rhs, on=['terms', 'arg_types', 'return_type', 'type'], how='outer')
        #     pms = pms.fillna(0)
        #     pms['count'] = pms['count_x'] - self.dw*pms['count_y'] # dw by default is 1
        #     pms = pms[pms['count']>=1][['terms', 'arg_types', 'return_type', 'type', 'count', 'log_prob']]

        # Unfold frames and filter with data
        pl = Task_lib(pms, self.dir_alpha)
        # pl.update_log_prob() if not (i==0&j==0) else None

        # Sample frames
        ns = 0
        filtered = pd.DataFrame({'terms': [], 'log_prob': [], 'n_exceptions': []})
        while (len(filtered)) < 1 and ns < 10000: # NOT TRUE ANYMORE: Safe to use a large ns, bc ground truth is covered - it will stop
          ns += 1
          if len(frames_left.index) <= frame_sample:
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
              passed_pm = all_programs.query(f'n_exceptions<={n_exceptions_allowed}')
              passed_pm['log_prob'] = passed_pm['log_prob'] - 2*passed_pm['n_exceptions'] # likelihood: exp(-2 * n_exceptions)
              print(f"[{iter_log}|{data_log}|{k}/{len(sampled_frames)}, -{ns}th] {sampled_frames.iloc[k].at['terms']}: {len(passed_pm)} passed") if logging else None
              filtered = filtered.append(passed_pm[['terms', 'log_prob', 'n_exceptions']], ignore_index=True)
        # Extract resusable bits
        if len(filtered) < 1:
          self.filtering_history[i][j] = 0
          print('Nothing consistent, skipping to next...') if logging else None
        else:
          self.filtering_history[i][j] = 1
          n_extract = len(filtered) if len(filtered) < top_n else top_n
          extracted = self.extract(filtered, n_extract, sample, base)
          print(extracted) if logging else None
          self.extraction_history[i][j] = extracted
          self.cur_programs = self.merge_lib(extracted)
          if len(save_prefix) > 0:
            padding = len(str(self.iter))
            pd.DataFrame.from_records(self.filtering_history).to_csv(f'{save_prefix}_filter_hist.csv')
            filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')
            self.cur_programs.to_csv(f'{save_prefix}_lib_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')

  def enum_hypos(self, frames, threshold='strict', logging=True, save_prefix=''):
    frames['prob'] = frames.apply(lambda row: math.exp(row['log_prob']), axis=1)
    for j in range(len(self.data)):
      # Preps
      data_log = f'Data {j+1}/{len(self.data)}'
      data = self.data[:(j+1)]
      # Unfold frames and filter with data
      pl = Task_lib(self.init_programs, self.dir_alpha)
      unfolded = pd.DataFrame(columns=['terms', 'log_prob', 'total_consistency', 'n_exceptions'])
      for k in range(len(frames)):
        programs = pl.unfold_programs_with_lp(frames.iloc[k].at['terms'], frames.iloc[k].at['log_prob'], data)
        for d in range(len(data)):
          programs[f'consistent_{d}'] = programs.apply(lambda row: pl.check_program(row['terms'], data[d]), axis=1)
        programs['total_consistency'] = programs[programs.columns[pd.Series(programs.columns).str.startswith('consistent')]].sum(axis=1)
        programs['n_exceptions'] = len(data) - programs['total_consistency']
        pc_programs = programs.query(f'total_consistency>0')
        pc_programs['log_prob'] = pc_programs['log_prob'] - 2*pc_programs['n_exceptions'] # likelihood: exp(-2 * n_exceptions)
        print(f"[{data_log}|{k}/{len(frames)}] {frames.iloc[k].at['terms']}: {len(pc_programs)} passed") if logging else None
        unfolded = unfolded.append(pc_programs[['terms', 'log_prob', 'total_consistency', 'n_exceptions']], ignore_index=True)
      # Extract resusable bits
      max_consistency = max(unfolded['total_consistency'])
      if threshold=='strict':
        con_thred = max_consistency
      elif threshold=='half':
        con_thred = max_consistency/2
      elif threshold=='min':
        con_thred = 1
      filtered = unfolded[unfolded['total_consistency']>=con_thred]
      filtered = filtered.drop_duplicates(subset=['terms'])
      extracted = self.extract(filtered, len(filtered), sample=False, base=0)
      extracted = extracted.drop_duplicates(subset=['terms'])
      print(f'{len(filtered)} filtered, {len(extracted)} extracted')
      self.cur_programs = self.merge_lib(extracted)
      if len(save_prefix) > 0:
        padding = len(str(self.iter))
        filtered.to_csv(f'{save_prefix}_filtered_{str(j+1).zfill(padding)}.csv')
        self.cur_programs.to_csv(f'{save_prefix}_lib_{str(j+1).zfill(padding)}.csv')

# %%
def df_to_data(df):
  task_data = []
  for i in range(len(df)):
    tdata = df.iloc[i].to_dict()
    task = {
      'agent': eval(tdata['agent']),
      'recipient': eval(tdata['recipient']),
      'result': eval(tdata['result'])
    }
    task_data.append(task)
  return task_data
