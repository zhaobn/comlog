
# %%
from os import getcwd
import random
import pandas as pd
import json
import sys
sys.path.append('..')

from base_terms import *
from base_classes import Program
from program_lib import Program_lib
from program_inf import Gibbs_sampler
from program_sim import *

# %% Task configs
tdata1_path = '../test_data/comp/training_1.json'
tdata2_path = '../test_data/comp/training_2.json'
gdata_path = '../test_data/comp/gen.json'
run_path = '../test_data/comp/comp_seq2/'
N_T_TASK = 15
N_G_TASK = 10
pm_init = pd.read_csv('../data/pm_init.csv', index_col=0, na_filter=False)

# %% Run experiments
with open(tdata1_path) as json_file:
  training_data_1 = [objstr_to_stone(d) for d in json.load(json_file)]

with open(tdata2_path) as json_file:
  training_data_2 = [objstr_to_stone(d) for d in json.load(json_file)]

with open(gdata_path) as json_file:
  gen_data = [objstr_to_stone(d) for d in json.load(json_file)]

# Training
pl = Gibbs_sampler(Program_lib(pm_init), training_data_2, iteration=100)
pl.run(save_prefix=f'{run_path}training_1/pm')

pl = Gibbs_sampler(Program_lib(pl.cur_programs), training_data_1, iteration=10)
pl.run(save_prefix=f'{run_path}training_2/pm')

# Prediction
preds = sim_for_all(gen_data, Program_lib(pl.cur_programs), 1000)
preds.to_csv(f'{run_path}preds.csv')
