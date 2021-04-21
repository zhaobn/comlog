import pandas as pd
import sys
sys.path.append('..')
sys.path.append('../..')
from base_terms import *
from base_classes import Program
from program_lib import Program_lib
from program_inf import Gibbs_sampler
from program_sim import *
data = pd.read_csv('../data/designs.csv', index_col=0, na_filter=False)
data = data.query('condition==1&component==2')
task_data = []
for i in range(len(data)):
  tdata = data.iloc[i].to_dict()
  tdata_fmt = {
    'agent': eval(tdata['agent']),
    'recipient': eval(tdata['recipient']),
    'result': eval(tdata['result'])
  }
  task_data.append(tdata_fmt)
pm_init = pd.read_csv('../data/pm_init_test.csv', index_col=0, na_filter=False)
pt = Gibbs_sampler(Program_lib(pm_init, 0.1), task_data, inc=False, iteration=4)
pt.run(save_prefix='r1_c2_bat_top1/pm', sample=False, top_n=1)