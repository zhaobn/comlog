# %%
iter = 500
test_configs = {
  'ft_row': "task_data_df.at[i,'trial'] in [1,2,3]",
  'ft_col': "task_data_df.at[i,'trial'] in [1,4,7]",
  'ft_ldg': "task_data_df.at[i,'trial'] in [1,5,9]",
  'ft_rdg': "task_data_df.at[i,'trial'] in [3,5,7]",
}
bash_scripts = ''

# %%
def generate_scripts(test_name, filter_condition, iteration=iter):
  process_data = """
    tdata = task_data_df.iloc[i].to_dict()
    task = {
      'agent': eval(tdata['agent']),
      'recipient': eval(tdata['recipient']),
      'result': eval(tdata['result'])
    }
    task_data.append(task)
  """
  return f"""
from task import *

task_data_df = pd.read_csv('data/task_data.csv')
task_data = []
for i in range(len(task_data_df)):
  if task_data_df.at[i,'phase']=='tab' and {filter_condition}:
    {process_data}
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
