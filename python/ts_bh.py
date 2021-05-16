# %%
from task import *

task_data_df = pd.read_csv('data/task_data.csv')
task_data_df = task_data_df[task_data_df.index>8]

task_data = []
for i in range(len(task_data_df)):
  tdata = task_data_df.iloc[i].to_dict()
  task = {
    'agent': eval(tdata['agent']),
    'recipient': eval(tdata['recipient']),
    'result': eval(tdata['result'])
  }
  task_data.append(task)

pm_init = pd.read_csv('data/task_pm.csv',index_col=0,na_filter=False)
all_frames = pd.read_csv('data/task_frames.csv',index_col=0)
g = Task_gibbs(Task_lib(pm_init), task_data, iteration=500)
g.fast_run(all_frames, sample=True, top_n=1, save_prefix='ts_bh/ts_bh')