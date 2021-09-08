# %%
import math
import numpy as np
import pandas as pd

from base_classes import Program
from base_terms import B,C,S,K,BB,BC,BS,BK,CB,CC,CS,CK,SB,SC,SS,SK,KB,KC,KS,KK
from program_lib import Program_lib
from program_inf import Gibbs_sampler
from helpers import args_to_string
from task_configs import *

# %%
class Task_lib(Program_lib):
  def __init__(self, df, dir_alpha=0.1):
    Program_lib.__init__(self, df, dir_alpha)

  @property
  def egg_lp(self):
    return min(self.get_all_objs()['log_prob'])

  @staticmethod
  def check_program(terms, data):
    result = Program(eval(terms)).run([data['agent'], data['recipient']])
    return result == data['result']

  def sample_base(self, type, add):
    if type == 'obj':
      stripe = self.sample_base('stripe', add)
      dot = self.sample_base('dot', add)
      egg = f'Egg({stripe},{dot})'
      return {'terms': egg, 'arg_types': '', 'return_type': 'egg', 'type': 'base_term'}
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
    eggs_df = pd.DataFrame({'terms': [], 'count':[]})
    stripe_df = self.content.query('return_type=="stripe"&type=="base_term"')
    dot_df = self.content.query('return_type=="dot"&type=="base_term"')
    for s in range(len(stripe_df)):
      for o in range(len(dot_df)):
        egg_feats = [
          stripe_df.iloc[s].at['terms'],
          dot_df.iloc[o].at['terms'],
        ]
        counts = [
          stripe_df.iloc[s].at['count'],
          dot_df.iloc[o].at['count'],
        ]
        eggs_df = eggs_df.append(pd.DataFrame({'terms': [f'Egg({",".join(egg_feats)})'], 'count': [sum(counts)]}), ignore_index=True)
    eggs_df['log_prob'] = self.log_dir(list(eggs_df['count']))
    return eggs_df[['terms', 'log_prob']]

  def unfold_program(self, terms, data):
    if terms[:2]=='PM':
      pm = eval(terms)
      unfolded = self.content.query(f'arg_types=="{args_to_string(pm.arg_types)}"&return_type=="{pm.return_type}"&type=="program"')
      if len(unfolded) > 0:
        return unfolded[['terms', 'log_prob']]
      else:
        return pd.DataFrame({'terms': [], 'log_prob': []})
    else:
      programs_list = []
      log_probs_list = []
      term_list = terms.split(',')
      for i in range(len(term_list)):
        t = term_list[i]
        tm = t.strip('[]')
        if tm in list(self.SET_MARKERS):
          unfolded = self.content.query(f'return_type=="{tm}"&type=="base_term"')
          unfolded_terms = list(unfolded['terms'])
          unfolded_lps = list(unfolded['log_prob'])
        elif tm == 'egg':
          unfolded_terms = [ data['agent'].name ]
          unfolded_lps = [ self.egg_lp ]
        elif 'PM' in tm:
          pm = eval(tm)
          qs = '&type=="program"' if (pm.arg_types == ['obj'] and pm.return_type == 'obj') else ''
          unfolded = self.content.query(f'arg_types=="{args_to_string(pm.arg_types)}"&return_type=="{pm.return_type}"{qs}')
          unfolded_terms = list(unfolded['terms'])
          unfolded_lps = list(unfolded['log_prob'])
        elif eval(tm).ctype == 'router':
          unfolded_terms = [tm]
          unfolded_lps = [0] # Taken care of by the frame base lp
        elif eval(tm).ctype == 'primitive':
          unfolded_terms = [tm]
          unfolded_lps = list(self.content.query(f'terms=="{tm}"&type=="primitive"').log_prob)
        else:
          print('Unknow term!')
        programs_list.append([t.replace(tm, u) for u in unfolded_terms])
        log_probs_list.append(unfolded_lps)
      return self.iter_compose_programs(programs_list, log_probs_list)

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
# t = [['egg', 'num'], 'num']

# rf = pl.typed_enum(t,1)
# rf.to_csv('data/task_frames.csv')

# rf2 = pl.typed_enum(t,2)
# rf2.to_csv('data/task_frames_2.csv')

# %%
class Task_gibbs(Gibbs_sampler):
  def __init__(self, program_lib, data_list, iteration, inc=True, burnin=0, down_weight=1, iter_start=0, data_start=0):
    Gibbs_sampler.__init__(self, program_lib, data_list, iteration, inc, burnin, down_weight, iter_start, data_start)
    self.all_programs = self.init_programs.copy()

  def merge_lib(self, extracted_df, target_df = None):
    if target_df is not None:
      merged_df = pd.merge(target_df.copy(), extracted_df, how='outer', on=['terms','arg_types','return_type','type']).fillna(0)
    else:
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
      data = self.data

      # Remove previously-extracted counts
      pms = self.cur_programs.copy()
      if i > 0:
        previous = self.extraction_history[i-1]
        if previous is not None:
          lhs = pms.copy()
          rhs = previous[['terms', 'arg_types', 'return_type', 'type', 'count']]
          pms = pd.merge(lhs, rhs, on=['terms', 'arg_types', 'return_type', 'type'], how='outer')
          pms = pms.fillna(0)
          pms['count'] = pms['count_x'] - self.dw*pms['count_y'] # dw by default is 1
          pms = pms[pms['count']>=1][['terms', 'arg_types', 'return_type', 'type', 'count', 'log_prob']]
      pl = Task_lib(pms, self.dir_alpha)

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
          all_programs = pl.unfold_programs_with_lp(sampled_frames.iloc[k].at['terms'], sampled_frames.iloc[k].at['log_prob'], data[0])
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
        self.filtering_history[i] = 0
        print('Nothing consistent, skipping to next...') if logging else None
      else:
        self.filtering_history[i] = 1
        n_extract = len(filtered) if len(filtered) < top_n else top_n
        extracted = self.extract(filtered, n_extract, sample, base)
        print(extracted) if logging else None
        self.extraction_history[i] = extracted
        self.cur_programs = self.merge_lib(extracted)
        if len(save_prefix) > 0:
          padding = len(str(self.iter))
          filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}.csv')
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
pl = Task_lib(pd.read_csv('data/task_pm.csv', index_col=0, na_filter=False))
g1 = Task_gibbs(pl, task_data['learn_a'], iteration=2)
g1.run(all_frames, top_n=1)

# %%
