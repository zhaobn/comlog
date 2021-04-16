
# %%
import pandas as pd
import sys
sys.path.append('..')
sys.path.append('../..')
from base_terms import *
from base_classes import Program
from program_lib import Program_lib
from program_inf import Gibbs_sampler
from program_sim import *

# %%
pm_init = pd.read_csv('../../data/pm_init_cut.csv', index_col=0, na_filter=False)
pl = Program_lib(pm_init, 0.1)
frames = pl.bfs([['obj', 'obj'], 'obj'],1)

data = pd.read_csv('design.csv')
for i in range(len(data)):
  task_data = data.iloc[i].to_dict()
  task_data_fmt = {
    'agent': eval(task_data['Agent']),
    'recipient': eval(task_data['Recipient']),
    'result': eval(task_data['Result'])
  }
  df = pl.filter_program(frames, task_data_fmt)
  df.to_csv(f'ran_{i}.csv')
