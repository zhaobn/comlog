
#%%
from numpy import true_divide
import pandas as pd

from task_configs import *
from task import *

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

# %%
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
# %%
