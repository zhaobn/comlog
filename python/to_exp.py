
# %%
import pandas as pd

# %%
task_csv = pd.read_csv('data/task_data.csv',index_col=0)

def translate_name(name):
  for r in (('Stone',''), ('(',''),(')','')):
    name = name.replace(*r)
  length = int(name.split(',')[1][1:])
  if name[:4] == 'Tria':
    edge = 3
  elif name[:4] == 'Rect':
    edge = 4
  elif name[:4] == 'Pent':
    edge = 5
  elif name[:4] == 'Hexa':
    edge = 6
  elif name[:4] == 'Hept':
    edge = 7
  return str(edge)+str(length)

task_csv['agent'] = task_csv.apply(lambda row: translate_name(row['agent']), axis=1)
task_csv['recipient'] = task_csv.apply(lambda row: translate_name(row['recipient']), axis=1)
task_csv['result'] = task_csv.apply(lambda row: translate_name(row['result']), axis=1)

# %%
task_csv.reset_index().to_json('data/task_exp_config.json', orient='records')
# %%
