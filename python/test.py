
from task import *

task_data_df = pd.read_csv('data/task_data.csv', na_filter=False)
sorted_indexes = [1, 5, 8]

task_data_df = task_data_df[task_data_df.index.isin(sorted_indexes)].reindex(sorted_indexes)
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
g.run(all_frames, save_prefix='test/nd_r2', sample=True, top_n=1)
