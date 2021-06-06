# %%
iter = 500
test_configs = {
  'nd_r1': [0,1,2],
  'nd_r2': [4,5,6],
  'nd_c1': [1,4,7],
  'nd_s4': [3,5,10],
  'nd_d1': [0,5,9],
  'nd_d2': [2,5,7],
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

task_data_df = pd.read_csv('data/task_data.csv', na_filter=False)
sorted_indexes = {filter_condition}

task_data_df = task_data_df[task_data_df.index.isin(sorted_indexes)].reindex(sorted_indexes)
task_data = []
for i in range(len(task_data_df)):
  {process_data}

pm_init = pd.read_csv('data/task_pm.csv',index_col=0,na_filter=False)
all_frames = pd.read_csv('data/task_frames.csv',index_col=0)
g = Task_gibbs(Task_lib(pm_init), task_data, iteration={iteration})
g.run(all_frames, save_prefix='test/{test_name}/{test_name}', sample=True, top_n=1)
"""

def generate_cmd(test_name):
  return f"""
mkdir test/{test_name}
screen -dmS {test_name} python {test_name}.py
"""

def generate_job(test_name):
  return f"""
#!/bin/sh
# Grid Engine options (lines prefixed with #$)
#$ -N {test_name}
#$ -cwd
#$ -l h_rt=02:00:00
#$ -l h_vmem=1G
#  These options are:
#  job name: -N
#  use the current working directory: -cwd
#  runtime limit of 5 minutes: -l h_rt
#  memory limit of 1 Gbyte: -l h_vmem

# Initialise the environment modules
module load anaconda
source activate comlog

python ../python/{test_name}.py
"""

def save_file(fname, fcontent, type='w'):
  f = open(fname, type)
  f.write(fcontent)
  f.close()


# %%
for item in test_configs.items():
  (test_name, trial_cond) = item
  scripts = generate_scripts(test_name, trial_cond)
  # print(scripts)
  save_file(f'{test_name}.py', scripts)
  bash_scripts += generate_cmd(test_name)

save_file('run.sh', bash_scripts)

# mkdir_cmds = ''
# qsub_cmds = ''

# for item in test_configs.items():
#   (test_name, trial_cond) = item
#   scripts = generate_scripts(test_name, trial_cond)
#   # print(scripts)
#   save_file(f'{test_name}.py', scripts)
#   mkdir_cmds += f'mkdir {test_name}\n'

#   job = generate_job(test_name)
#   save_file(f'run_{test_name}.sh', job)
#   qsub_cmds += (f'qsub run_{test_name}.sh\n')

# print(mkdir_cmds)
# print(qsub_cmds)

# %%
