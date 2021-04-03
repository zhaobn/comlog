
# %%
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
main_path = '../test_data/bootstrapping_top/'
tdata_path = main_path + 'training.json'
ldata_path = main_path + 'learning.json'
gdata_path = main_path + 'gen.json'
N_T_TASK = 30
N_L_TASK = 5
N_G_TASK = 10
pm_init = pd.read_csv('../data/pm_init.csv', index_col=0, na_filter=False)

# %% Run experiments
with open(tdata_path) as json_file:
  training_data = [objstr_to_stone(d) for d in json.load(json_file)]

with open(ldata_path) as json_file:
  learning_data = [objstr_to_stone(d) for d in json.load(json_file)]

with open(gdata_path) as json_file:
  gen_data = [objstr_to_stone(d) for d in json.load(json_file)]

# Training
pt = Gibbs_sampler(Program_lib(pm_init), training_data, iteration=2)
pt.run(save_prefix=f'{main_path}training/pm', sample=False, top_n=2)

# Learning
pl = Gibbs_sampler(Program_lib(pt.cur_programs), learning_data, iteration=2)
pl.run(save_prefix=f'{main_path}learning/pm', sample=False, top_n=2)

# Prediction
preds = sim_for_all(gen_data, Program_lib(pl.cur_programs), 10000)
preds.to_csv(f'{main_path}preds.csv')
