
from task import *
iter = 2

# Prep data
task_data_df = pd.read_csv('data/task_data.csv', na_filter=False)
phase_indexes = [2, 15, 32, 11, 23, 35]
task_phase = task_data_df[task_data_df.index.isin(phase_indexes)].reindex(phase_indexes)

all_frames = pd.read_csv('data/task_frames.csv',index_col=0)

# Task phase 1
pm_init = pd.read_csv('data/task_pm.csv',index_col=0,na_filter=False)
g1 = Task_gibbs(Task_lib(pm_init), df_to_data(task_phase), iteration=iter)
g1.run(all_frames, save_prefix='test/inc_3/ti', sample=True, top_n=5, exceptions_allowed=3)
