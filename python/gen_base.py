
#%%
import numpy as np
import pandas as pd
import math
import random
import itertools

from task_configs import *
from task import *

from helpers import normalize, softmax

# %%
stripes = list(range(5)) # [0,1,2,3,4]
dots = list(range(5))
init_len = list(range(1,5)) # [1,2,3,4]
all_len = list(range(4*4+1)) # 0 ~ 16

all_agents = []
all_recipients = []
all_results = []

# Stone(Stripe, Dot, Length)
for s in stripes:
  for d in dots:
    agent = (s,d,1)
    all_agents.append(agent)

for l in init_len:
  recipient = (0,0,l)
  all_recipients.append(recipient)

for l in all_len:
  result = (0,0,l)
  all_results.append(result)

all_pairs = []
for a in all_agents:
  for r in all_recipients:
    all_pairs.append({
      'agent': f'Stone(S{a[0]},O{a[1]},L{a[2]})',
      'recipient': f'Stone(S{r[0]},O{r[1]},L{r[2]})',
    })

all_pairs_df = pd.DataFrame.from_dict(all_pairs)
all_pairs_df = all_pairs_df.assign(ground_truth=0,model_alt=0,model_heur=0,random_choice=1)
# all_pairs_df.to_csv('data/gen_pairs.csv')

all_pairs_df = pd.read_csv('data/gen_pairs.csv', index_col=0)

ground_truth = Program([SS,[KK,setLength,Stone(S0,O0,L3)],[SC,[BB,subnn,[CB,[B,mulnn,getStripe],getLength]],getDot]])
model_alt = Program([SS,[BK,setLength,[B,I,[S,[K,setLength,Stone(S0,O0,L2)],getLength]]],[CB,[B,mulnn,getStripe],getLength]])
model_heur = Program([BK,[setLength,Stone(S0,O0,L3)],[B,[subnn,3],getDot]])

# # %% Prep
# all_obs_df = pd.DataFrame(columns=['pair_index', 'agent', 'recipient', 'result', 'ground_truth', 'model_alt', 'model_heur', 'random_choice'])

# all_results_stones = [ f'Stone(S{r[0]},O{r[1]},L{r[2]})' for r in all_results ]
# all_rs_df_k0 = pd.DataFrame({'key':[0]*len(all_results_stones), 'result': all_results_stones})

# for i in all_pairs_df.index:
#   pair_index = i
#   agent = all_pairs_df.iloc[i].agent
#   recipient = all_pairs_df.iloc[i].recipient
#   data = [ eval(agent), eval(recipient) ]

#   sub_df = (
#     pd.DataFrame({'key':[0], 'pair_index':[i], 'agent': [agent], 'recipient': [recipient]})
#     .merge(all_rs_df_k0, on='key', how='outer')
#     .drop(['key'], axis=1)
#   )

#   sub_df['ground_truth'] = sub_df.apply(lambda row: int(row['result']==ground_truth.run(data).name), axis=1)
#   sub_df['model_alt'] = sub_df.apply(lambda row: int(row['result']== model_alt.run(data).name), axis=1)
#   sub_df['model_heur'] = sub_df.apply(lambda row: int(row['result']==model_heur.run(data).name), axis=1)
#   sub_df['random_choice'] = 1

#   all_obs_df = all_obs_df.append(sub_df, ignore_index=True)

# all_obs_df.to_csv('data/gen_obs.csv')

# # %% Information Gain
# all_obs_df = pd.read_csv('data/gen_obs.csv', index_col=0)
# all_obs_df = all_obs_df.assign(IG_4=0., IG_gh=0., IG_ga=0., IG_gr=0., IG_nr=0., IG_na=0. )

# def kl_sub (a, b):
#   if a == 0:
#     return 0
#   else:
#     return a * math.log(a/b)

# for i in all_obs_df.index:
#   all_obs_df.at[i, 'IG_4'] = sum([kl_sub(a,b) for (a,b) in list(zip(
#     normalize(list(all_obs_df.iloc[i][['ground_truth', 'model_alt', 'model_heur', 'random_choice']])),
#     [1/4] * 4
#   ))])
#   all_obs_df.at[i, 'IG_gh'] = sum([kl_sub(a,b) for (a,b) in list(zip(
#     normalize(list(all_obs_df.iloc[i][['ground_truth', 'model_heur']])),
#     [1/2] * 2
#   ))])
#   all_obs_df.at[i, 'IG_ga'] = sum([kl_sub(a,b) for (a,b) in list(zip(
#     normalize(list(all_obs_df.iloc[i][['ground_truth', 'model_alt']])),
#     [1/2] * 2
#   ))])
#   all_obs_df.at[i, 'IG_gr'] = sum([kl_sub(a,b) for (a,b) in list(zip(
#     normalize(list(all_obs_df.iloc[i][['ground_truth', 'random_choice']])),
#     [1/2] * 2
#   ))])
#   all_obs_df.at[i, 'IG_nr'] = sum([kl_sub(a,b) for (a,b) in list(zip(
#     normalize(list(all_obs_df.iloc[i][['ground_truth', 'model_alt', 'model_heur']])),
#     [1/3] * 3
#   ))])
#   all_obs_df.at[i, 'IG_na'] = sum([kl_sub(a,b) for (a,b) in list(zip(
#     normalize(list(all_obs_df.iloc[i][['ground_truth', 'model_heur', 'random_choice']])),
#     [1/3] * 3
#   ))])


# all_pairs_ig = all_obs_df.groupby(['agent', 'recipient'])[['IG_4', 'IG_gh', 'IG_ga', 'IG_gr', 'IG_nr', 'IG_na']].sum().reset_index()

# # %% Pick trials
# trials = []
# target_n = 8

# IG_values = list(set(all_pairs_ig['IG_4']))
# IG_values.sort(reverse=True)

# all_pairs_ig_sorted = (
#   all_obs_df
#   .groupby(['agent', 'recipient'])[['IG_4']]
#   .sum()
#   .reset_index()
#   .sort_values(by='IG_4', ascending=False)
# )

# ag_sort = (
#   all_pairs_ig_sorted
#   .groupby(['agent','IG_4'])['recipient']
#   .apply(lambda x: ';'.join(x))
#   .reset_index()
#   .sort_values(by='IG_4', ascending=False)
# )

# max_ig = IG_values[0]
# max_ig_df = ag_sort[ag_sort['IG_4']==max_ig]
# len(max_ig_df.index) # 4, smaller than target_n

# for i in max_ig_df.index:
#   trials.append({
#     'agent': max_ig_df.at[i, 'agent'],
#     'recipient': random.choice(max_ig_df.at[i, 'recipient'].split(';')),
#     'IG_4': max_ig_df.at[i, 'IG_4'],
#   })


# sec_max_ig = IG_values[1]
# sec_max_ig_df = ag_sort[ag_sort['IG_4']==sec_max_ig]
# len(sec_max_ig_df.index) # 19, 4 + 19 > target_n

# # Remove apeared agents
# sec_max_ig_df_cut = sec_max_ig_df[~sec_max_ig_df['agent'].isin([a['agent'] for a in trials])]
# len(sec_max_ig_df_cut.index)  # 17, 4 + 17 > target_n

# demo_appeared = [
#   'Stone(S1,O0,L1)','Stone(S2,O0,L1)','Stone(S3,O0,L1)',
#   'Stone(S1,O3,L1)','Stone(S2,O2,L1)','Stone(S3,O1,L1)',
# ]
# sec_max_ig_df_cut = sec_max_ig_df_cut[~sec_max_ig_df_cut['agent'].isin(demo_appeared)]
# len(sec_max_ig_df_cut.index)  # 14, 4 + 14 > target_n


# sec_sampled_df = sec_max_ig_df_cut.sample(n=(target_n - len(trials)))
# for i in sec_sampled_df.index:
#   trials.append({
#     'agent': sec_sampled_df.at[i, 'agent'],
#     'recipient': random.choice(sec_sampled_df.at[i, 'recipient'].split(';')),
#     'IG_4': sec_sampled_df.at[i, 'IG_4'],
#   })

# trials_df = pd.DataFrame(trials)
# trials_df.to_csv('data/_gen_trials.csv')

# # %% Try complimentary data points
# all_obs_df = pd.read_csv('data/gen_obs.csv', index_col=0)

# df = all_obs_df[all_obs_df['pair_index']==0]

# def agg_preds (df):
#   preds = list(df['ground_truth']) + list(df['model_alt']) + list(df['model_heur']) + list(df['random_choice'])
#   return ''.join([str(x) for x in preds])

# all_pairs_agg = all_pairs_df[['agent', 'recipient']]
# all_pairs_agg['preds'] = ''
# all_pairs_agg['pair_index'] = all_pairs_agg.index
# for i in all_pairs_agg.index:
#   all_pairs_agg.at[i,'preds'] = agg_preds(all_obs_df[all_obs_df['pair_index']==i])

# all_pairs_agg_info = all_pairs_agg.groupby('preds')['pair_index'].apply(lambda x: ','.join([str(i) for i in x])).reset_index()


# # %% Try another complimentary calc.
# all_obs_df = pd.read_csv('data/gen_obs.csv', index_col=0)
# all_obs_df['IG'] = 0.
# all_obs_df['random_choice'] = 1/len(all_results)

# def kl_sub (a, b):
#   if a == 0:
#     return 0
#   else:
#     return a * math.log(a/b)
# for i in all_obs_df.index:
#   all_obs_df.at[i, 'IG'] = sum([kl_sub(a,b) for (a,b) in list(zip(
#     normalize(list(all_obs_df.iloc[i][['ground_truth', 'model_alt', 'model_heur', 'random_choice']])),
#     normalize([5,2,3,1])
#   ))])

# def weight_result(row):
#   preds = list(zip(
#     [row['ground_truth'], row['model_alt'], row['model_heur'], row['random_choice']],
#     normalize([5,2,3,1])
#   ))
#   return sum([a*b for (a,b) in preds])
# all_obs_df['weight'] = all_obs_df.apply(lambda row: weight_result(row), axis=1)

# # Aggregrate
# all_pairs_igg = all_pairs_df[['agent', 'recipient']]
# all_pairs_igg['IG'] = 0.

# for i in all_pairs_igg.index:
#   df = all_obs_df[all_obs_df['pair_index']==i]
#   all_pairs_igg.at[i,'IG'] = sum(df['IG'] * df['weight'])

# ig_vals = list(set([round(x, 4) for x in all_pairs_igg['IG']])) # 5 elements
# all_pairs_igg['ig_class'] = all_pairs_igg.apply(lambda row: ig_vals.index(round(row['IG'],4)), axis=1)

# all_pairs_igg['pair_index'] = all_pairs_igg.index
# all_pairs_igg_grouped = all_pairs_igg.groupby(['ig_class'])['pair_index'].apply(lambda x: ','.join([str(i) for i in x])).reset_index()

# all_pairs_igg['IG_rounded'] = round(all_pairs_igg['IG'], 4)
# all_pairs_igg_grouped = pd.merge(
#   all_pairs_igg.groupby(['ig_class', 'IG_rounded']).size().reset_index(),
#   all_pairs_igg_grouped, how='left', on='ig_class'
# )[['ig_class', 'IG_rounded_x', '0_x', 'pair_index']].rename(columns={
#   'IG_rounded_x': 'IG',
#   '0_x': 'count',
#   'pair_index': 'pair_indices'
# })
# all_pairs_igg_grouped.to_csv('data/gen_info.csv')

# %% Test by simulation
all_obs_df = pd.read_csv('data/gen_obs.csv', index_col=0)
all_pairs_igg_grouped = pd.read_csv('data/gen_info.csv', index_col=0)

combos = list(itertools.combinations_with_replacement(all_pairs_igg_grouped['ig_class'], 9))
combo_df = pd.DataFrame({'combo': [','.join([str(i) for i in list(x)]) for x in combos]})

def safe_log_div(x, y):
  return 0 if x==0 else math.log(x/y, 2)

def safe_log_mult(x):
  return 0 if x==0 else x * math.log(x, 2)

def sim_gt(hypo, pair_ids, n, noise=1):
  ret_data = pd.DataFrame(columns=['pair_index', 'agent', 'recipient', 'result', 'count'])
  for pi in pair_ids:
    data = all_obs_df[all_obs_df['pair_index']==pi][['pair_index', 'agent', 'recipient', 'result', hypo]]
    data['prob'] = softmax(data[hypo], noise)
    data['count'] = 0
    i = 0
    while i < n:
      data.at[data.sample(1, weights='prob').index[0], 'count'] += 1
      i += 1
    ret_data = ret_data.append(data[['pair_index', 'agent', 'recipient', 'result', 'count']])
  return ret_data
# sim_gt('ground_truth', [3], n=20, noise=4)

def get_igs(combo_list):
  total_df = all_obs_df[['pair_index', 'agent', 'recipient', 'result', 'ground_truth', 'model_alt', 'model_heur', 'random_choice']]
  prior_entropy = -1 * sum(safe_log_mult(i) for i in [1/4] * 4)

  # Prep data
  class_ids = [ int(i) for i in combo_list.split(',') ]
  pair_ids = []
  for i in class_ids:
    can_pairs = all_pairs_igg_grouped[all_pairs_igg_grouped['ig_class']==i]['pair_indices']
    can_pair_ids = [ int(i) for i in list(can_pairs)[0].split(',') ]
    this_pair_id = random.choice(can_pair_ids)
    pair_ids.append(this_pair_id)

  # Run sim
  eig_info = {'combo': [combo_list]}
  for hypo in ['ground_truth', 'model_alt', 'model_heur', 'random_choice']: #, , 'random_choice'
    sim_counts = sim_gt(hypo, pair_ids, 20, 4)
    post_df = pd.merge(sim_counts, total_df, how='left', on=['pair_index', 'agent', 'recipient', 'result'])
    post_pp = []
    for s_hypo in ['ground_truth', 'model_alt', 'model_heur', 'random_choice']:
      hc = post_df[['count', s_hypo]]
      hc = hc[hc['count']>0]
      hc['pp'] = hc.apply(lambda row: row[s_hypo] ** row['count'], axis=1)
      post_pp.append(sum(hc['pp'] ))
    post_pp_normalized = normalize(post_pp)
    # eig_info[hypo] = [-sum([ a * safe_log_div(b, a) for (a, b) in list(zip([1/4]*4, post_pp_normalized))])]
    eig_info[hypo] = prior_entropy - (-1 * sum(safe_log_mult(i) for i in post_pp_normalized))
  return pd.DataFrame.from_dict(eig_info)


# combo_igs = pd.DataFrame(columns=['combo', 'ground_truth', 'model_alt', 'model_heur', 'random_choice'])
# for ci in combo_df.index:
#   sub_igs = get_igs(combo_df.at[ci, 'combo'])
#   combo_igs = combo_igs.append(sub_igs)
#   combo_igs.to_csv('data/gen_combo_igs.csv')

# # %% Check combo igs
# combo_igs = pd.read_csv('data/gen_combo_igs.csv', index_col=0)
# combo_igs['total'] = combo_igs['ground_truth'] +  combo_igs['model_alt'] + combo_igs['model_heur'] +  combo_igs['random_choice']
# combo_igs['total'] = round(combo_igs['total']/4, 4)

# %% Loop through first 10 for 10 times
combo_igs = pd.read_csv('data/gen_combo_igs.csv', index_col=0)

# plt.figure()
# combo_igs.sort_values('total', ascending=False)['total'].plot(kind="bar")
# combo_igs.total.quantile(0.98)

combo_igs_to_check = combo_igs.sort_values('total', ascending=False).head(35)[['combo']].reset_index(drop=True)

def get_sim_ig(df, x):
  ret_df =  pd.DataFrame(columns=['combo', 'ground_truth', 'model_alt', 'model_heur', 'random_choice'])
  for i in df.index:
    sub_igs = get_igs(df.at[i, 'combo'])
    ret_df = ret_df.append(sub_igs, ignore_index=True)
  total_col = f'total_{str(x)}'
  ret_df[total_col] = ret_df['ground_truth'] +  ret_df['model_alt'] + ret_df['model_heur'] +  ret_df['random_choice']
  ret_df[total_col] = round(ret_df[total_col]/4, 4)
  return ret_df[['combo', total_col]]


for x in range(10):
  combo_igs_looped = combo_igs_to_check.merge(get_sim_ig(combo_igs_to_check, x), how='left', on='combo')
  combo_igs_looped.to_csv('data/gen_combo_further.csv')

# %%
combo_igs_looped = pd.read_csv('data/gen_combo_further.csv', index_col=0)
combo_igs_looped['total'] = combo_igs_looped[list(combo_igs_looped)[1:]].sum(axis=1)
