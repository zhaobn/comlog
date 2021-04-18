
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
data = pd.read_csv('design.csv', index_col=0)
data = data.query('Task==2')
task_data = []
for i in range(len(data)):
  tdata = data.iloc[i].to_dict()
  tdata_fmt = {
    'agent': eval(tdata['Agent']),
    'recipient': eval(tdata['Recipient']),
    'result': eval(tdata['Result'])
  }
  task_data.append(tdata_fmt)

# %%
pm_init = pd.read_csv('../../data/pm_init_cut.csv', index_col=0, na_filter=False)
pt = Gibbs_sampler(Program_lib(pm_init, 0.1), task_data, iteration=1)
pt.run(save_prefix='phase_2/pm', top_n=4, sample=False)
