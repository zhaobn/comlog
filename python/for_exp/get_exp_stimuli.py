
# %%
import pandas as pd

# %%
stripes = [0,1,2,3,4]
dots = [0,1,2,3,4]
init_len = [1,2,3,4]

all_agents = []
all_recipients = []

trials = []

# %%
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
    if rp_len >= 0 and rp_len <= 12:
      trials.append({
        'agent': str(a),
        'recipient': str(r),
        'result': str((0,0,rp_len))
      })

trials_df = pd.DataFrame.from_dict(trials)
trials_df['trial_id'] = trials_df.index + 1
trials_df = trials_df.set_index('trial_id')
trials_df.to_csv('trials.csv')
trials_df.reset_index().to_json('../for_exp/config.json', orient='records')

# %%
def translate_name(name):
  if len(name) < 1:
    return ''
  else:
    for r in (('Stone',''), ('(',''),(')',''), ('S',''), ('O',''), ('L','')):
      name = name.replace(*r)
    vals = name.split(',')
    return f'({vals[0]}, {vals[1]}, {vals[2]})'
# translate_name('Stone(S4,O3,L1)')

# %%
trials_df = pd.read_csv('trials.csv')

learn_a = pd.DataFrame({
  'agent': ["(1, 0, 1)", "(2, 0, 1)", "(3, 0, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 2)", "(0, 0, 1)"],
  'result': ["(0, 0, 3)", "(0, 0, 4)", "(0, 0, 3)"],
})
learn_b = pd.DataFrame({
  'agent': ["(1, 3, 1)", "(2, 2, 1)", "(3, 1, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 2)", "(0, 0, 1)"],
  'result': ["(0, 0, 0)", "(0, 0, 2)", "(0, 0, 2)"],
})
gen = pd.read_csv('inv_trials.csv', index_col=0).rename(columns={'agent': 'agent_stone','recipient': 'recipient_stone'})
gen['agent'] = gen.apply(lambda row: translate_name(row['agent_stone']), axis=1)
gen['recipient'] = gen.apply(lambda row: translate_name(row['recipient_stone']), axis=1)
gen_trials = pd.merge(gen, trials_df, how='left', on=['agent', 'recipient']).dropna()

learn_a_ids = list(pd.merge(learn_a, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [7, 20, 37]
learn_b_ids = list(pd.merge(learn_b, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [16, 28, 41]
gen_ids = [int(x) for x in list(gen_trials.sort_values(by='EIG', ascending=False).head(8)['trial_id'])]
# [58, 67, 10, 62, 18, 8, 6, 68]
