
from task import *

task_data_df = pd.read_csv('data/task_data.csv', na_filter=False)
phase_1_indexes = [2, 15, 32]
phase_2_indexes = [11, 23, 35]

task_phase_1 = task_data_df[task_data_df.index.isin(phase_1_indexes)].reindex(phase_1_indexes)
task_phase_2 = task_data_df[task_data_df.index.isin(phase_2_indexes)].reindex(phase_2_indexes)

pm_init = pd.read_csv('data/task_pm.csv',index_col=0,na_filter=False)
all_frames = pd.read_csv('data/task_frames.csv',index_col=0)

g1 = Task_gibbs(Task_lib(pm_init), df_to_data(task_phase_1), iteration=1000)
g1.run(all_frames, save_prefix='test/inc_1/ti', sample=True, top_n=1)

pm_init_new = g1.cur_programs
g2 = Task_gibbs(Task_lib(pm_init_new), df_to_data(task_phase_2), iteration=1000)
g2.run(all_frames, save_prefix='test/inc_2/ti', sample=True, top_n=1)
