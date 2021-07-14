
#%%
import numpy as np
import pandas as pd
import math
import random

from task_configs import *
from task import *

from helpers import normalize

# %%
stripes = list(range(5)) # [0,1,2,3,4]
dots = list(range(5))
init_len = list(range(1,5)) # [1,2,3,4]
all_len = list(range(4*4+1)) # 0 ~ 16

all_agents = []
all_recipients = []
all_results = []

# %%
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
all_pairs_df.to_csv('data/gen_pairs.csv')

# %%
all_pairs_df = pd.read_csv('data/gen_pairs.csv', index_col=0)

ground_truth = Program([SS,[KK,setLength,Stone(S0,O0,L3)],[SC,[BB,subnn,[CB,[B,mulnn,getStripe],getLength]],getDot]])
model_alt = Program([SS,[BK,setLength,[B,I,[S,[K,setLength,Stone(S0,O0,L2)],getLength]]],[CB,[B,mulnn,getStripe],getLength]])
model_heur = Program([BK,[setLength,Stone(S0,O0,L3)],[B,[subnn,3],getDot]])

# %% Prep
all_obs_df = pd.DataFrame(columns=['pair_index', 'agent', 'recipient', 'result', 'ground_truth', 'model_alt', 'model_heur', 'random_choice'])

all_results_stones = [ f'Stone(S{r[0]},O{r[1]},L{r[2]})' for r in all_results ]
all_rs_df_k0 = pd.DataFrame({'key':[0]*len(all_results_stones), 'result': all_results_stones})

for i in all_pairs_df.index:
  pair_index = i
  agent = all_pairs_df.iloc[i].agent
  recipient = all_pairs_df.iloc[i].recipient
  data = [ eval(agent), eval(recipient) ]

  sub_df = (
    pd.DataFrame({'key':[0], 'pair_index':[i], 'agent': [agent], 'recipient': [recipient]})
    .merge(all_rs_df_k0, on='key', how='outer')
    .drop(['key'], axis=1)
  )

  sub_df['ground_truth'] = sub_df.apply(lambda row: int(row['result']==ground_truth.run(data).name), axis=1)
  sub_df['model_alt'] = sub_df.apply(lambda row: int(row['result']== model_alt.run(data).name), axis=1)
  sub_df['model_heur'] = sub_df.apply(lambda row: int(row['result']==model_heur.run(data).name), axis=1)
  sub_df['random_choice'] = 1

  all_obs_df = all_obs_df.append(sub_df, ignore_index=True)

all_obs_df.to_csv('data/gen_obs.csv')

# %% Information Gain
all_obs_df = pd.read_csv('data/gen_obs.csv', index_col=0)
all_obs_df = all_obs_df.assign(IG_4=0., IG_gh=0., IG_ga=0., IG_gr=0., IG_nr=0., IG_na=0. )

def kl_sub (a, b):
  if a == 0:
    return 0
  else:
    return a * math.log(a/b)

for i in all_obs_df.index:
  all_obs_df.at[i, 'IG_4'] = sum([kl_sub(a,b) for (a,b) in list(zip(
    normalize(list(all_obs_df.iloc[i][['ground_truth', 'model_alt', 'model_heur', 'random_choice']])),
    [1/4] * 4
  ))])
  all_obs_df.at[i, 'IG_gh'] = sum([kl_sub(a,b) for (a,b) in list(zip(
    normalize(list(all_obs_df.iloc[i][['ground_truth', 'model_heur']])),
    [1/2] * 2
  ))])
  all_obs_df.at[i, 'IG_ga'] = sum([kl_sub(a,b) for (a,b) in list(zip(
    normalize(list(all_obs_df.iloc[i][['ground_truth', 'model_alt']])),
    [1/2] * 2
  ))])
  all_obs_df.at[i, 'IG_gr'] = sum([kl_sub(a,b) for (a,b) in list(zip(
    normalize(list(all_obs_df.iloc[i][['ground_truth', 'random_choice']])),
    [1/2] * 2
  ))])
  all_obs_df.at[i, 'IG_nr'] = sum([kl_sub(a,b) for (a,b) in list(zip(
    normalize(list(all_obs_df.iloc[i][['ground_truth', 'model_alt', 'model_heur']])),
    [1/3] * 3
  ))])
  all_obs_df.at[i, 'IG_na'] = sum([kl_sub(a,b) for (a,b) in list(zip(
    normalize(list(all_obs_df.iloc[i][['ground_truth', 'model_heur', 'random_choice']])),
    [1/3] * 3
  ))])


all_pairs_ig = all_obs_df.groupby(['agent', 'recipient'])[['IG_4', 'IG_gh', 'IG_ga', 'IG_gr', 'IG_nr', 'IG_na']].sum().reset_index()

# %% Pick trials
trials = []
target_n = 8

IG_values = list(set(all_pairs_ig['IG_4']))
IG_values.sort(reverse=True)

all_pairs_ig_sorted = (
  all_obs_df
  .groupby(['agent', 'recipient'])[['IG_4']]
  .sum()
  .reset_index()
  .sort_values(by='IG_4', ascending=False)
)

ag_sort = (
  all_pairs_ig_sorted
  .groupby(['agent','IG_4'])['recipient']
  .apply(lambda x: ';'.join(x))
  .reset_index()
  .sort_values(by='IG_4', ascending=False)
)

max_ig = IG_values[0]
max_ig_df = ag_sort[ag_sort['IG_4']==max_ig]
len(max_ig_df.index) # 4, smaller than target_n

for i in max_ig_df.index:
  trials.append({
    'agent': max_ig_df.at[i, 'agent'],
    'recipient': random.choice(max_ig_df.at[i, 'recipient'].split(';')),
    'IG_4': max_ig_df.at[i, 'IG_4'],
  })

sec_max_ig = IG_values[1]
sec_max_ig_df = ag_sort[ag_sort['IG_4']==sec_max_ig]
len(sec_max_ig_df.index) # 19, 4 + 19 > target_n

sec_sampled_df = sec_max_ig_df.sample(n=(target_n - len(trials)))
for i in sec_sampled_df.index:
  trials.append({
    'agent': sec_sampled_df.at[i, 'agent'],
    'recipient': random.choice(sec_sampled_df.at[i, 'recipient'].split(';')),
    'IG_4': sec_sampled_df.at[i, 'IG_4'],
  })

trials_df = pd.DataFrame(trials)
trials_df

# %%


# %% Pick trials...
'','agent','recipient','IG_4'
0,'Stone(S0,O3,L1)','Stone(S0,O0,L2)',22.180710
1,'Stone(S0,O4,L1)','Stone(S0,O0,L1)',22.180710
2,'Stone(S1,O0,L1)','Stone(S0,O0,L3)',22.180710
3,'Stone(S3,O0,L1)','Stone(S0,O0,L1)',22.180710
4,'Stone(S3,O1,L1)','Stone(S0,O0,L1)',21.775245
5,'Stone(S1,O0,L1)','Stone(S0,O0,L4)',21.775245
6,'Stone(S0,O0,L1)','Stone(S0,O0,L1)',21.775245
7,'Stone(S2,O0,L1)','Stone(S0,O0,L2)',21.775245
