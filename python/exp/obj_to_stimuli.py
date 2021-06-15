
# %%
from task import Task_lib
import pandas as pd

# %%
task_csv = pd.read_csv('../data/task_data.csv', na_filter=False)
task_csv = task_csv.drop(['phase'], axis=1)
task_csv['trial'] = task_csv.index + 1
task_csv = task_csv.set_index('trial')
# %%
def translate_name(name):
  if len(name) < 1:
    return ''
  else:
    for r in (('Stone',''), ('(',''),(')','')):
      name = name.replace(*r)
    stripes = int(name.split(',')[1][1:])
    length = int(name.split(',')[2][1:])
    # if name[:4] == 'Tria':
    #   stripes = 3
    # elif name[:4] == 'Rect':
    #   edge = 4
    # elif name[:4] == 'Pent':
    #   edge = 5
    # elif name[:4] == 'Hexa':
    #   edge = 6
    # elif name[:4] == 'Hept':
    #   edge = 7
    return str(stripes)+str(length)

task_csv['agent'] = task_csv.apply(lambda row: translate_name(row['agent']), axis=1)
task_csv['recipient'] = task_csv.apply(lambda row: translate_name(row['recipient']), axis=1)
task_csv['result'] = task_csv.apply(lambda row: translate_name(row['result']), axis=1)
# %%
task_csv.reset_index().to_json('../exp/exp_config.json', orient='records')
# %%
