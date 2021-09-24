
# %%
import math
import numpy as np
import pandas as pd
pd.set_option('mode.chained_assignment', None)

from task_terms_extra import *
from helpers import secure_list, names_to_string, print_name, normalize, softmax
from program_lib import Program_lib_light, Program_lib

# %%
class Gibbs_sampler:
  def __init__(self, program_lib, data_list, iteration, burnin=0, down_weight=1):
    self.cur_programs = program_lib.content
    self.local_programs = program_lib.content
    self.data = data_list
    self.dw = down_weight
    self.iter = iteration
    self.burnin = burnin

  # Frames => programs consistent with data
  def find_programs(self, frames, pm_lib, data, iter_log, frame_sample=20, fs_cap=100, exceptions_allowed=0):
    data = secure_list(data)
    pl = Program_lib(pm_lib)
    frames_left = frames.copy()
    filtered = pd.DataFrame({'terms': [], 'log_prob': [], 'n_exceptions': []})
    ns = 0
    while (len(filtered)) < 1 and ns < fs_cap+1:
      ns += 1
      # Sample frames
      if len(frames_left) <= frame_sample:
        sampled_frames = frames_left.copy()
      else:
        sampled_frames = frames_left.sample(n=frame_sample, weights='prob').reset_index(drop=True)
      frames_left = frames_left[~frames_left['terms'].isin(sampled_frames['terms'])]
      for k in range(len(sampled_frames)):
        # Unfold programs wrt current library
        all_programs = pl.unfold_programs_with_lp(sampled_frames.iloc[k].at['terms'], sampled_frames.iloc[k].at['log_prob'], data)
        # Filter consistency wrt learning data
        if len(all_programs) > 0:
          for d in range(len(data)):
            all_programs[f'consistent_{d}'] = all_programs.apply(lambda row: pl.check_program(row['terms'], data[d]), axis=1)
          all_programs['total_consistency'] = all_programs[all_programs.columns[pd.Series(all_programs.columns).str.startswith('consistent')]].sum(axis=1)
          all_programs['n_exceptions'] = len(data) - all_programs['total_consistency']
          passed_pm = all_programs.query(f'n_exceptions<={exceptions_allowed}')
          passed_pm['log_prob'] = passed_pm['log_prob'] - 2*passed_pm['n_exceptions'] # likelihood: exp(-2 * n_exceptions)
          print(f"[{iter_log}|{k}/{len(sampled_frames)}, -{ns}th] {sampled_frames.iloc[k].at['terms']}: {len(passed_pm)} passed") if len(iter_log)>0 else None
          filtered = filtered.append(passed_pm[['terms', 'log_prob', 'n_exceptions']], ignore_index=True)
    return filtered

  # Sample extracted programs for reuse
  def sample_extraction(self, filtered, top_n=1, sample=True, base=0):
    if len(filtered) <= top_n or sample == 0:
      to_add = filtered.copy()
    else:
      filtered['prob'] = filtered.apply(lambda row: math.exp(row['log_prob']), axis=1)
      filtered['prob'] = normalize(filtered['prob']) if base == 0 else softmax(filtered['prob'], base)
      to_add = filtered.sample(n=top_n, weights='prob')
    # Prep extraction in required format
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
    return extracted

  # Add extracted programs to library
  def merge_lib(self, extracted_df, target_df=None):
    base_df = self.cur_programs.copy() if target_df is None else target_df
    merged_df = pd.merge(base_df, extracted_df, how='outer', on=['terms','arg_types','return_type','type']).fillna(0)
    # Increase counter
    merged_df['count'] = merged_df['count_x'] + merged_df['count_y']
    set_df = (merged_df
      .query('count_x>0')[['terms','arg_types','return_type','type','is_init','count','comp_lp','adaptor_lp','log_prob_x']]
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
    return temp_lib.content.copy()

  # Main sampling procedure
  def run(self, frames, top_n=1, sample=True, frame_sample=20, fs_cap=100, base=0, logging=True, save_prefix='', exceptions_allowed=0):
    frames['prob'] = frames.apply(lambda row: math.exp(row['log_prob']), axis=1)
    for i in range(self.iter):
      iter_log = f'Iter {i+1}/{self.iter}' if logging else ''
      filtered = self.find_programs(frames, self.cur_programs.copy(), self.data, iter_log, frame_sample, fs_cap, exceptions_allowed)
      # Extract resusable bits
      if len(filtered) < 1:
        print('Nothing consistent, skipping to next...') if logging else None
      else:
        extracted = self.sample_extraction(filtered, top_n, sample, base)
        print(extracted) if logging else None
        self.cur_programs = self.merge_lib(extracted)
        # Save intermediate samples, optional
        if len(save_prefix) > 0:
          padding = len(str(self.iter))
          filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}.csv')
          extracted.to_csv(f'{save_prefix}_extracted_{str(i+1).zfill(padding)}.csv')
          self.cur_programs.to_csv(f'{save_prefix}_lib_{str(i+1).zfill(padding)}.csv')

  @staticmethod
  def combine_libs(lib_1, lib_2):
    combined = pd.merge(lib_1, lib_2, on=['terms','arg_types','return_type','type'], how='outer').fillna(0)
    combined['is_init'] = combined.apply(lambda row: max(row['is_init_x'], row['is_init_y']), axis=1)
    combined['count'] = combined.apply(lambda row: max(row['count_x'], row['count_y']), axis=1)
    combined['comp_lp'] = combined.apply(lambda row: min(row['comp_lp_x'], row['comp_lp_y']), axis=1)
    combined['adaptor_lp'] = combined.apply(lambda row: min(row['adaptor_lp_x'], row['adaptor_lp_y']), axis=1)
    combined['log_prob'] = combined.apply(lambda row: min(row['log_prob_x'], row['log_prob_y']), axis=1)
    return combined[['terms','arg_types','return_type','type','is_init','count','comp_lp','adaptor_lp','log_prob']]

  # Local iteration
  def local_run(self, frames, top_n=1, sample=True, frame_sample=20, fs_cap=1000, base=0, logging=True, save_prefix='', exceptions_allowed=0):
    frames['prob'] = frames.apply(lambda row: math.exp(row['log_prob']), axis=1)

    for i in range(self.iter):
      for j in range(len(self.data)):
        local_data = secure_list(self.data[j])
        iter_log = f'Iter {i+1}/{self.iter}|data {j+1}/{len(self.data)}' if logging else ''
        local_filtered = self.find_programs(frames, self.local_programs.copy(), local_data, iter_log, frame_sample, fs_cap, exceptions_allowed)
        if len(local_filtered) < 1:
          print('Nothing consistent, skipping to next...') if logging else None
        else:
          extracted = self.sample_extraction(local_filtered, top_n, sample, base)
          print(extracted) if logging else None
          self.local_programs = self.merge_lib(extracted, self.local_programs)
        if j > 0:
          until_data = self.data[:j+1]
          iter_log = f'Iter {i+1}/{self.iter}|up to {j+1}/{len(self.data)}' if logging else ''
          temp_lib = self.combine_libs(self.cur_programs.copy(), self.local_programs.copy())
          filtered = self.find_programs(frames, temp_lib, until_data, iter_log, frame_sample, fs_cap, exceptions_allowed)
          if len(filtered) < 1:
            print('Nothing consistent, skipping to next...') if logging else None
          else:
            extracted = self.sample_extraction(filtered, top_n, sample, base)
            print(extracted) if logging else None
            self.cur_programs = self.merge_lib(extracted)
          if len(save_prefix) > 0:
            padding = len(str(self.iter))
            filtered.to_csv(f'{save_prefix}_filtered_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')
            extracted.to_csv(f'{save_prefix}_extracted_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')
            self.cur_programs.to_csv(f'{save_prefix}_lib_{str(i+1).zfill(padding)}_{str(j+1).zfill(padding)}.csv')


# # %% Debug
# all_data = pd.read_json('for_exp/config.json')
# task_ids = {
#   'learn_a': [23, 42, 61],
#   'learn_b': [35, 50, 65],
#   'gen': [82, 8, 20, 4, 98, 48, 71, 40],
# }
# task_ids['gen'].sort()

# task_data = {}
# for item in task_ids:
#   task_data[item] = []
#   for ti in task_ids[item]:
#     transformed = {}
#     data = all_data[all_data.trial_id==ti]
#     _, agent, recipient, result = list(data.iloc[0])
#     transformed['agent'] = eval(f'Egg(S{agent[1]},O{agent[4]})')
#     transformed['recipient'] = int(recipient[-2])
#     transformed['result'] = int(result[-2])
#     task_data[item].append(transformed)

# all_frames = pd.read_csv('data/task_frames.csv',index_col=0)
# data_len_a = len(task_data['learn_a'])
# data_len_b = len(task_data['learn_b'])

# # %%
# pl = Program_lib(pd.read_csv('data/task_pm.csv', index_col=0, na_filter=False))
# g1 = Gibbs_sampler(pl, task_data['learn_a'], iteration=2)

# all_frames = pd.read_csv('data/task_frames_extended.csv',index_col=0)
# pl = Program_lib(pd.read_csv('data/task_pm_extended.csv', index_col=0, na_filter=False))
# frames = all_frames
# frames['prob'] = frames.apply(lambda row: math.exp(row['log_prob']), axis=1)
# data = task_data['learn_a']
# top_n=1
# sample=True
# frame_sample=20
# base=0
# logging=True
# save_prefix=''
# exceptions_allowed=0
# iter_log = ''
# fs_cap=100

# # %%
# all_frames = pd.read_csv('data/task_frames.csv',index_col=0)
# pl = Program_lib(pd.read_csv('data/task_pm.csv', index_col=0, na_filter=False))
# g1 = Gibbs_sampler(pl, task_data['learn_a'], iteration=3)
# g1.run(all_frames, top_n=1, save_prefix='test/tt')

# # %%
# all_frames = pd.read_csv('data/task_frames_extended.csv',index_col=0)
# pl = Program_lib(pd.read_csv('data/task_pm_extended.csv', index_col=0, na_filter=False))
# g1 = Gibbs_sampler(pl, task_data['learn_b'], iteration=3)
# g1.run(all_frames, top_n=1, save_prefix='test/tt')

# # %%
# all_frames = pd.read_csv('data/task_frames_extended.csv',index_col=0)
# pl = Program_lib(pd.read_csv('data/task_pm_extended.csv', index_col=0, na_filter=False))
# g1 = Gibbs_sampler(pl, task_data['learn_b'], iteration=3)
# g1.local_run(all_frames, top_n=1, save_prefix='test/tt')


# %%
