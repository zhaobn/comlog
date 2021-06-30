
# %%
from numpy import int32
import pandas as pd

# %%
stripes = [1,2,3,4]
dots = [0,1,2,3,4]
init_len = [1,2,3,4]

all_agents = []
all_recipients = []

trials = []

for s in stripes:
  for d in dots:
    agent = (s,d,1)
    all_agents.append(agent)

for l in init_len:
  recipient = (0,0,l)
  all_recipients.append(recipient)

for a in all_agents:
  for r in all_recipients:
    rp_len = r[2] * a[0] - a[1]
    if rp_len >= 0 and rp_len <= 10:
      trials.append({
        'agent': a,
        'recipient': r,
        'result': (0,0,rp_len)
      })

trials_df = pd.DataFrame.from_dict(trials)
trials_df['trial_id'] = trials_df.index + 1
trials_df = trials_df.set_index('trial_id')
trials_df.to_csv('trials.csv')

# %%
trials_df = pd.read_csv('trials_labeled.csv', index_col=0).fillna(0).astype({"subs": int, 'subs_pd': int, 'subd': int})
trials_df.to_csv('trials_labeled.csv')
trials_df.reset_index().to_json('exp_config.json', orient='records')

# %%
