#%%
import numpy as np
import pandas as pd
import math
import random
import itertools

import sys
sys.path.append('../')
from task_configs import *
from task import *
from helpers import normalize, softmax

# %% Global vars
CAND_PROGRAMS = pd.read_csv('../for_exp/full_inc_eqc.csv', index_col=0)
N_PROGRAMS = len(CAND_PROGRAMS)
ALL_PAIRS = pd.read_csv('../data/gen_pairs.csv', index_col=0)
ALL_OBS = pd.read_csv('../data/gen_obs.csv', index_col=0)[['pair_index', 'agent', 'recipient', 'result']]

PM_LL = ALL_OBS.copy()
for i in CAND_PROGRAMS.index:
  PM_LL[f'pm_{str(i)}'] = 0
  preds = CAND_PROGRAMS.at[i, 'pred_list'].split(',')
  for pi in range(len(ALL_PAIRS)):
    predicted_idx = PM_LL[(PM_LL['pair_index']==pi)&(PM_LL['result']==f'Stone(S0,O0,L{preds[pi]})')].index[0]
    PM_LL.at[predicted_idx, f'pm_{str(i)}'] = 1

# %%
def get_sim(program_id, pair_ids, n=20, noise=5):
  ret_data = pd.DataFrame(columns=['pair_index', 'agent', 'recipient', 'result', 'count'])
  for pi in pair_ids:
    data = PM_LL[PM_LL['pair_index']==pi][['pair_index', 'agent', 'recipient', 'result', program_id]]
    data['prob'] = softmax(data[program_id], noise)
    data['count'] = 0
    i = 0
    while i < n:
      data.at[data.sample(1, weights='prob').index[0], 'count'] += 1
      i += 1
    ret_data = ret_data.append(data[['pair_index', 'agent', 'recipient', 'result', 'count']])
  return ret_data
# get_sim('pm_4', [3,7], n=20, noise=4)

def conditional_entropy(sim_data, noise=5, weights=None, sample=False):
  post_pp = []
  for mi in range(len(CAND_PROGRAMS)): # If sample, check just a few of programs
    pm_id = f'pm_{mi}'
    pm_counts = sim_data[['count', pm_id]]
    pm_counts['ll'] = softmax(pm_counts[pm_id], noise)
    pm_counts = pm_counts[pm_counts['count']>0]
    pm_counts['pp'] = pm_counts.apply(lambda row: row['ll'] ** row['count'], axis=1)
    post_pp.append(sum(pm_counts['pp']))
  post_pp = normalize(post_pp) # If weighted, use weighted normalization
  return -sum([x * math.log(x) for x in post_pp])

# %%
trials_df = pd.DataFrame(columns=['pair_index', 'agent', 'recipient','EIG'])
# # For the sake of testing
# CAND_PROGRAMS = CAND_PROGRAMS.sample(3)
# N_PROGRAMS = len(CAND_PROGRAMS)
prior_entropy = -1 * N_PROGRAMS * (1/N_PROGRAMS) * math.log((1/N_PROGRAMS)) #TODO: Use weighted prior?

# Get learned pair indices
task_data_df = pd.read_csv('../data/task_data.csv', na_filter=False)
phase_indexes = [2, 15, 32, 11, 23, 35]
task_phase = task_data_df[task_data_df.index.isin(phase_indexes)].reindex(phase_indexes)
task_df = pd.merge(task_phase, ALL_PAIRS, how='left', on=['agent', 'recipient'])
learned_pairs = list(task_df['pair_index'])


# Get the first one
candidate_pairs = ALL_PAIRS[~ALL_PAIRS['pair_index'].isin(learned_pairs)].reset_index(drop=True)
pair_eigs = []
for pi in range(len(candidate_pairs)):
  info_gain = []
  for mi in range(len(CAND_PROGRAMS)):
    pm_id = f'pm_{mi}'
    sim_counts = get_sim(pm_id, [pi])
    pm_lls = PM_LL[PM_LL['pair_index']==pi]
    post_df = pd.merge(sim_counts, pm_lls, how='left', on=['pair_index', 'agent', 'recipient', 'result'])
    info_gain.append(prior_entropy - conditional_entropy(post_df))
  pair_eigs.append(sum(info_gain)/len(info_gain)) # Average information gain, no weighting

best_pair = candidate_pairs[candidate_pairs.index==pair_eigs.index(max(pair_eigs))]
best_pair['EIG'] = max(pair_eigs)
trials_df = trials_df.append(best_pair, ignore_index=True)

# Build greedily
while (len(trials_df) < 20):
  prev_pair_ids = list(trials_df['pair_index'])
  candidate_pairs = candidate_pairs[~candidate_pairs['pair_index'].isin(prev_pair_ids)].reset_index(drop=True)
  pair_eigs = []
  for pi in range(len(candidate_pairs)):
    info_gain = []
    for mi in range(len(CAND_PROGRAMS)):
      pm_id = f'pm_{mi}'
      sim_counts = get_sim(pm_id, prev_pair_ids+[pi])
      pm_lls = PM_LL[PM_LL['pair_index'].isin(prev_pair_ids+[pi])]
      post_df = pd.merge(sim_counts, pm_lls, how='left', on=['pair_index', 'agent', 'recipient', 'result'])
      info_gain.append(prior_entropy - conditional_entropy(post_df))
    pair_eigs.append(sum(info_gain)/len(info_gain)) # Average information gain, no weighting
  best_pair = candidate_pairs[candidate_pairs.index==pair_eigs.index(max(pair_eigs))]
  best_pair['EIG'] = max(pair_eigs)
  trials_df = trials_df.append(best_pair, ignore_index=True)

trials_df.to_csv('../test/inc_trials.csv')
