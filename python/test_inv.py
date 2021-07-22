
from task import *

# Prep data
task_data_df = pd.read_csv('data/task_data.csv', na_filter=False)
phase_indexes = [11, 23, 35, 2, 15, 32]
task_phase = task_data_df[task_data_df.index.isin(phase_indexes)].reindex(phase_indexes)
all_frames = pd.read_csv('data/task_frames.csv',index_col=0)

# %%
pl = Task_lib(pd.read_csv('data/task_pm.csv', index_col=0, na_filter=False))
g1 = Task_gibbs(pl, df_to_data(task_phase))
g1.enum_hypos(all_frames, save_prefix='test/inv/eh')
