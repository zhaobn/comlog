# %%
iter = 200
test_configs = {
  'moc': "task_data = task_row + task_col",
  'mor': "task_data = task_row + task_rdg",
  'mol': "task_data = task_row + task_ldg",
  'mco': "task_data = task_col + task_row",
  'mcr': "task_data = task_col + task_rdg",
  'mcl': "task_data = task_col + task_ldg",
  'mro': "task_data = task_rdg + task_row",
  'mrc': "task_data = task_rdg + task_col",
  'mrl': "task_data = task_rdg + task_ldg",
  'mlo': "task_data = task_ldg + task_row",
  'mlc': "task_data = task_ldg + task_col",
  'mlr': "task_data = task_ldg + task_rdg",
  'mcor': "task_data = task_col + task_row + task_rdg",
}
# test_configs = {
#   'ft_row': "task_data_df.at[i,'trial'] in [1,2,3]",
#   'ft_col': "task_data_df.at[i,'trial'] in [1,4,7]",
#   'ft_ldg': "task_data_df.at[i,'trial'] in [1,5,9]",
#   'ft_rdg': "task_data_df.at[i,'trial'] in [3,5,7]",
# }
bash_scripts = ''

# %%
def generate_scripts(test_name, filter_condition, iteration=iter):
  defs = """
task_data_df = pd.read_csv('data/task_data.csv')

def get_task_task(tids, dsource=task_data_df):
  task_data = []
  for i in range(len(dsource)):
    if dsource.at[i,'phase']=='tab' and dsource.at[i,'trial'] in tids:
      tdata = dsource.iloc[i].to_dict()
      task = {
        'agent': eval(tdata['agent']),
        'recipient': eval(tdata['recipient']),
        'result': eval(tdata['result'])
      }
      task_data.append(task)
  return task_data

task_row = get_task_task([1,2,3])
task_col = get_task_task([1,4,7])
task_ldg = get_task_task([1,5,9])
task_rdg = get_task_task([3,5,7])

  """
  # process_data = """
  #   tdata = task_data_df.iloc[i].to_dict()
  #   task = {
  #     'agent': eval(tdata['agent']),
  #     'recipient': eval(tdata['recipient']),
  #     'result': eval(tdata['result'])
  #   }
  #   task_data.append(task)
  # """
  return f"""
from task import *

{defs}
{filter_condition}
pm_init = pd.read_csv('data/task_pm.csv',index_col=0,na_filter=False)
all_frames = pd.read_csv('data/task_frames.csv',index_col=0)
g = Task_gibbs(Task_lib(pm_init), task_data, iteration={iteration})
g.fast_run(all_frames, save_prefix='{test_name}/{test_name}', sample=True, top_n=1)
"""

def generate_cmd(test_name):
  return f"""
mkdir {test_name}
screen -dmS {test_name} python {test_name}.py
"""

def save_file(fname, fcontent, type='w'):
  f = open(fname, type)
  f.write(fcontent)
  f.close()


for item in test_configs.items():
  (test_name, trial_cond) = item
  scripts = generate_scripts(test_name, trial_cond)
  # print(scripts)
  save_file(f'{test_name}.py', scripts)
  bash_scripts += generate_cmd(test_name)

save_file('run.sh', bash_scripts)

# %%
