
# %%
import pandas as pd

# %%
def translate_name(name):
  if isinstance(name, str):
    for r in (('Egg',''), ('(',''),(')',''), ('S',''), ('O','')):
      name = name.replace(*r)
    vals = name.split(',')
    return f'({vals[0]}, {vals[1]}, 1)'
  elif isinstance(name, int):
    return f'(0, 0, {str(name)})'
  else:
    return ''
# translate_name('Egg(S4,O3)')
# translate_name(1)


# %% Experiment 1
stripes = [0,1,2,3,4]
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
    rp_len = 0 if rp_len < 0 else rp_len
    rp_len = 16 if rp_len > 16 else rp_len
    trials.append({
      'agent': str(a),
      'recipient': str(r),
      'result': str((0,0,rp_len))
    })

trials_df = pd.DataFrame.from_dict(trials)
trials_df['trial_id'] = trials_df.index + 1
trials_df = trials_df.set_index('trial_id')
trials_df.reset_index().to_json('config.json', orient='records')

# %% Get Experiment 1 trials
trials_df = pd.read_json('config.json')

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
learn_c = pd.DataFrame({
  'agent': ["(1, 1, 1)", "(1, 2, 1)", "(1, 3, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 3)", "(0, 0, 3)"],
  'result': ["(0, 0, 2)", "(0, 0, 1)", "(0, 0, 0)"],
})
gen = pd.read_csv('../trials/data/final_trials.csv', index_col=0).rename(columns={'agent': 'agent_stone','recipient': 'recipient_stone'})
gen['agent'] = gen.apply(lambda row: translate_name(row['agent_stone']), axis=1)
gen['recipient'] = gen.apply(lambda row: translate_name(row['recipient_stone']), axis=1)
gen_trials = pd.merge(gen, trials_df, how='left', on=['agent', 'recipient']).dropna()

learn_a_ids = list(pd.merge(learn_a, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [23, 42, 61]
learn_b_ids = list(pd.merge(learn_b, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [35, 50, 65]
learn_c_ids = list(pd.merge(learn_c, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [27, 31, 35]
gen_ids = [int(x) for x in list(gen_trials['trial_id'])]
# [100, 71, 78, 55, 47, 83, 9, 3]

# %% Experiment 2
for s in stripes:
  for d in dots:
    agent = (s,d,1)
    all_agents.append(agent)

for l in init_len:
  recipient = (0,0,l)
  all_recipients.append(recipient)

for a in all_agents:
  for r in all_recipients:
    rp_len = r[2] * a[1] - a[0]
    rp_len = 0 if rp_len < 0 else rp_len
    rp_len = 16 if rp_len > 16 else rp_len
    trials.append({
      'agent': str(a),
      'recipient': str(r),
      'result': str((0,0,rp_len))
    })

trials_df = pd.DataFrame.from_dict(trials)
trials_df['trial_id'] = trials_df.index + 1
trials_df = trials_df.set_index('trial_id')
trials_df.reset_index().to_json('config_2.json', orient='records')

# %% Get Experiment 2 trials
trials_df = pd.read_json('config_2.json')

learn_a = pd.DataFrame({
  'agent': ["(0, 1, 1)", "(0, 2, 1)", "(0, 3, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 2)", "(0, 0, 1)"],
  'result': ["(0, 0, 3)", "(0, 0, 4)", "(0, 0, 3)"],
})
learn_b = pd.DataFrame({
  'agent': ["(3, 1, 1)", "(2, 2, 1)", "(1, 3, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 2)", "(0, 0, 1)"],
  'result': ["(0, 0, 0)", "(0, 0, 2)", "(0, 0, 2)"],
})
learn_c = pd.DataFrame({
  'agent': ["(1, 1, 1)", "(2, 1, 1)", "(3, 1, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 3)", "(0, 0, 3)"],
  'result': ["(0, 0, 2)", "(0, 0, 1)", "(0, 0, 0)"],
})
gen = pd.read_csv('../trials/data/final_trials_2.csv', index_col=0).rename(columns={'agent': 'agent_stone','recipient': 'recipient_stone'})
gen['agent'] = gen.apply(lambda row: translate_name(row['agent_stone']), axis=1)
gen['recipient'] = gen.apply(lambda row: translate_name(row['recipient_stone']), axis=1)
gen_trials = pd.merge(gen, trials_df, how='left', on=['agent', 'recipient']).dropna()

learn_a_ids = list(pd.merge(learn_a, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [7, 10, 13]
learn_b_ids = list(pd.merge(learn_b, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [67, 50, 33]
learn_c_ids = list(pd.merge(learn_c, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [27, 47, 67]
gen_ids = [int(x) for x in list(gen_trials['trial_id'])]
# [100, 55, 94, 71, 31, 19, 41, 3]

# %% Tentative Experiment 3
stripes = [0,1,2,3,4]
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
    rp_len = a[0] * (r[2] - a[1])
    rp_len = 0 if rp_len < 0 else rp_len
    # rp_len = 16 if rp_len > 16 else rp_len
    trials.append({
      'agent': str(a),
      'recipient': str(r),
      'result': str((0,0,rp_len))
    })

trials_df = pd.DataFrame.from_dict(trials)
trials_df['trial_id'] = trials_df.index + 1
trials_df = trials_df.set_index('trial_id')
trials_df.reset_index().to_json('config_3.json', orient='records')

# %% Get tentative Experiment 3 trials
trials_df = pd.read_json('config_3.json')

learn_sub = pd.DataFrame({
  'agent': ["(1, 3, 1)", "(1, 2, 1)", "(1, 1, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 3)", "(0, 0, 3)"],
  'result': ["(0, 0, 0)", "(0, 0, 1)", "(0, 0, 2)"],
})
learn_both = pd.DataFrame({
  'agent': ["(1, 3, 1)", "(2, 2, 1)", "(3, 1, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 3)", "(0, 0, 3)"],
  'result': ["(0, 0, 0)", "(0, 0, 2)", "(0, 0, 6)"],
})
learn_mult = pd.DataFrame({
  'agent': ["(1, 0, 1)", "(2, 0, 1)", "(3, 0, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 3)", "(0, 0, 3)"],
  'result': ["(0, 0, 3)", "(0, 0, 6)", "(0, 0, 9)"],
})
gen = pd.read_csv('../trials/data/final_trials.csv', index_col=0).rename(columns={'agent': 'agent_stone','recipient': 'recipient_stone'})
gen['agent'] = gen.apply(lambda row: translate_name(row['agent_stone']), axis=1)
gen['recipient'] = gen.apply(lambda row: translate_name(row['recipient_stone']), axis=1)
gen_trials = pd.merge(gen, trials_df, how='left', on=['agent', 'recipient']).dropna()

learn_sub_ids = list(pd.merge(learn_sub, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [35, 31, 27]
learn_mult_ids = list(pd.merge(learn_mult, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [23, 43, 63]
learn_both_ids = list(pd.merge(learn_both, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [35, 51, 67]
gen_ids = [int(x) for x in list(gen_trials['trial_id'])]
# [100, 71, 78, 55, 47, 83, 9, 3]

# %% Pilot 2
stripes = [0,1,2,3,4]
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
    rp_len = a[0] * (r[2] - a[1])
    rp_len = 0 if rp_len < 0 else rp_len
    # alternative
    rp_alt = a[0] * r[2] - a[1]
    rp_alt = 0 if rp_alt < 0 else rp_alt
    trials.append({
      'agent': str(a),
      'recipient': str(r),
      'result': str((0,0,rp_len)),
      'alter': str((0,0,rp_alt))
    })

trials_df = pd.DataFrame.from_dict(trials)
trials_df['trial_id'] = trials_df.index + 1
trials_df = trials_df.set_index('trial_id')
trials_df.reset_index().to_json('config_4.json', orient='records')

# %% Get Pilot 2 trials
trials_df = pd.read_json('config_4.json')

learn_mult = pd.DataFrame({
  'agent': ["(1, 0, 1)", "(2, 0, 1)", "(3, 0, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 2)", "(0, 0, 1)"],
  'result': ["(0, 0, 3)", "(0, 0, 4)", "(0, 0, 3)"],
})
learn_sub = pd.DataFrame({
  'agent': ["(1, 1, 1)", "(1, 2, 1)", "(1, 3, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 3)", "(0, 0, 3)"],
  'result': ["(0, 0, 2)", "(0, 0, 1)", "(0, 0, 0)"],
})

gen = pd.read_csv('../trials/data/final_trials_flip.csv', index_col=0).rename(columns={'agent': 'agent_stone','recipient': 'recipient_stone'})
gen['agent'] = gen.apply(lambda row: translate_name(row['agent_stone']), axis=1)
gen['recipient'] = gen.apply(lambda row: translate_name(row['recipient_stone']), axis=1)
gen_trials = pd.merge(gen, trials_df, how='left', on=['agent', 'recipient']).dropna()

learn_mult_ids = list(pd.merge(learn_mult, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [23, 42, 61]
learn_sub_ids = list(pd.merge(learn_sub, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [27, 31, 35]
gen_ids = [int(x) for x in list(gen_trials['trial_id'])]
# [100, 91, 78, 55, 47, 83, 9, 3]

# %% Get Experiment 3 trials
trials_df = pd.read_json('config_4.json')

learn_mult = pd.DataFrame({
  'agent': ["(1, 0, 1)", "(2, 0, 1)", "(3, 0, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 2)", "(0, 0, 1)"],
  'result': ["(0, 0, 3)", "(0, 0, 4)", "(0, 0, 3)"],
})
learn_sub = pd.DataFrame({
  'agent': ["(1, 1, 1)", "(1, 2, 1)", "(1, 3, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 3)", "(0, 0, 3)"],
  'result': ["(0, 0, 2)", "(0, 0, 1)", "(0, 0, 0)"],
})

gen = pd.read_csv('../trials/data/final_trials.csv', index_col=0).rename(columns={'agent': 'agent_stone','recipient': 'recipient_stone'})
gen['agent'] = gen.apply(lambda row: translate_name(row['agent_stone']), axis=1)
gen['recipient'] = gen.apply(lambda row: translate_name(row['recipient_stone']), axis=1)
gen_trials = pd.merge(gen, trials_df, how='left', on=['agent', 'recipient']).dropna()

learn_mult_ids = list(pd.merge(learn_mult, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [23, 42, 61]
learn_sub_ids = list(pd.merge(learn_sub, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [27, 31, 35]
gen_ids = [int(x) for x in list(gen_trials['trial_id'])]
# [100, 71, 78, 55, 47, 83, 9, 3]


# %% Experiment 4
stripes = [0,1,2,3,4]
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
    rp_len = a[1] * (r[2] - a[0])
    rp_len = 0 if rp_len < 0 else rp_len
    # alternative
    rp_alt = a[1] * r[2] - a[0]
    rp_alt = 0 if rp_alt < 0 else rp_alt
    trials.append({
      'agent': str(a),
      'recipient': str(r),
      'result': str((0,0,rp_len)),
      'alter': str((0,0,rp_alt))
    })

trials_df = pd.DataFrame.from_dict(trials)
trials_df['trial_id'] = trials_df.index + 1
trials_df = trials_df.set_index('trial_id')
trials_df.reset_index().to_json('config_5.json', orient='records')

# %% Get Experiment 4 trials
trials_df = pd.read_json('config_5.json')

learn_mult = pd.DataFrame({
  'agent': ["(0, 1, 1)", "(0, 2, 1)", "(0, 3, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 2)", "(0, 0, 1)"],
  'result': ["(0, 0, 3)", "(0, 0, 4)", "(0, 0, 3)"],
})
learn_sub = pd.DataFrame({
  'agent': ["(1, 1, 1)", "(2, 1, 1)", "(3, 1, 1)"],
  'recipient': ["(0, 0, 3)", "(0, 0, 3)", "(0, 0, 3)"],
  'result': ["(0, 0, 2)", "(0, 0, 1)", "(0, 0, 0)"],
})
gen = pd.read_csv('../trials/data/final_trials_2.csv', index_col=0).rename(columns={'agent': 'agent_stone','recipient': 'recipient_stone'})
gen['agent'] = gen.apply(lambda row: translate_name(row['agent_stone']), axis=1)
gen['recipient'] = gen.apply(lambda row: translate_name(row['recipient_stone']), axis=1)
gen_trials = pd.merge(gen, trials_df, how='left', on=['agent', 'recipient']).dropna()

learn_mult_ids = list(pd.merge(learn_mult, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [7, 10, 13]
learn_sub_ids = list(pd.merge(learn_sub, trials_df, how='left', on=['agent', 'recipient', 'result'])['trial_id'])
# [27, 47, 67]
gen_ids = [int(x) for x in list(gen_trials['trial_id'])]
# [100, 55, 94, 71, 31, 19, 41, 3]

# %%
